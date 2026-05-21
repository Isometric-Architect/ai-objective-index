from __future__ import annotations

from collections import Counter
import re
from typing import Any

from ai_objective_index.integrated_store import get_store_for_scope
from ai_objective_index.store import ObjectiveIndexStore

from .probe_card import ProbeCard, ProbePlan, ProbeReceipt, ProbeReceiptAggregate, ProbeResult


CRITICAL_FIELDS = {
    "privacy_policy",
    "data_retention_policy",
    "commercial_use_terms",
    "pricing",
    "docs_url",
}

CLAIM_ALLOW_CONTEXT = ("not ", "no ", "without ", "cannot ", "must not ", "do not ", "does not ", "un")


def _store_for_scope(data_scope: str) -> ObjectiveIndexStore | None:
    try:
        return get_store_for_scope(data_scope)
    except Exception:
        return None


def _object_id(capability_id: str, object_id: str | None = None) -> str:
    return object_id or capability_id.removeprefix("capability:")


def _object_text(obj: Any) -> str:
    if obj is None:
        return ""
    payload = obj.model_dump(mode="json") if hasattr(obj, "model_dump") else dict(obj)
    return " ".join(str(value) for value in payload.values()).lower()


def _contains_positive_phrase(text: str, phrase: str) -> bool:
    normalized = text.lower()
    phrase = phrase.lower()
    pattern = re.compile(rf"(?<![a-z0-9_-]){re.escape(phrase)}(?![a-z0-9_-])")
    for match in pattern.finditer(normalized):
        prefix = normalized[max(0, match.start() - 24) : match.start()]
        if any(prefix.endswith(context) for context in CLAIM_ALLOW_CONTEXT):
            continue
        return True
    return False


def _result(card: ProbeCard, token: str, findings: list[str] | None = None, warnings: list[str] | None = None, errors: list[str] | None = None, refs: list[str] | None = None, checked: list[str] | None = None) -> ProbeResult:
    return ProbeResult(
        probe_id=card.probe_id or "probe-missing-id",
        capability_id=card.capability_id,
        result=token,  # type: ignore[arg-type]
        checked_fields=checked or card.required_fields,
        findings=findings or [],
        warnings=warnings or [],
        errors=errors or [],
        evidence_refs=refs or [],
    )


def run_probe_card(card: ProbeCard) -> ProbeResult:
    if not (
        card.sandbox_policy.no_network
        and card.sandbox_policy.no_external_tool_execution
        and card.sandbox_policy.no_subprocess
        and card.sandbox_policy.local_data_only
    ):
        return _result(card, "INVALID_PROBE", errors=["Probe sandbox policy must remain local-only with no network, tools, or subprocess."])

    if card.probe_type == "negative_control":
        text = _object_text(card.canary_input or {})
        if any(_contains_positive_phrase(text, claim) for claim in card.forbidden_claims):
            return _result(card, "BLOCK_UNSUPPORTED_CLAIM", findings=["Negative control unsupported claim was blocked."])
        return _result(card, "FAIL_EXPECTED_NEGATIVE_CONTROL", errors=["Negative control did not trigger expected block."])

    store = _store_for_scope(card.data_scope)
    if store is None:
        return _result(card, "HOLD_INSUFFICIENT_EVIDENCE", warnings=[f"Data scope unavailable: {card.data_scope}"])

    obj_id = _object_id(card.capability_id, card.object_id)
    obj = store.get_object(obj_id)
    if obj is None:
        return _result(card, "HOLD_INSUFFICIENT_EVIDENCE", warnings=[f"Capability object not found: {obj_id}"])
    traces = store.get_traces(obj_id)
    missing = [item.field for item in store.list_missing_fields(obj_id)]
    obj_text = _object_text(obj)

    if card.probe_type == "source_trace_integrity":
        if not traces:
            return _result(card, "HOLD_INSUFFICIENT_EVIDENCE", warnings=["No local source traces found."], checked=["source_trace_ids"])
        return _result(
            card,
            "PASS_LOCAL",
            findings=[f"{len(traces)} local source traces found."],
            refs=[trace.trace_id for trace in traces],
            checked=["source_trace_ids"],
        )

    if card.probe_type == "missing_field_check":
        critical = sorted(set(missing) & set(card.required_fields or CRITICAL_FIELDS))
        if critical:
            return _result(card, "HOLD_MISSING_FIELDS", findings=[f"Critical missing fields: {', '.join(critical)}"], checked=critical)
        return _result(card, "PASS_LOCAL", findings=["No requested critical missing fields found."], checked=card.required_fields)

    if card.probe_type in {"policy_clarity_check", "docs_presence_check", "repository_presence_check", "license_presence_check"}:
        if card.probe_type == "policy_clarity_check":
            policy_missing = sorted(set(missing) & {"privacy_policy", "data_retention_policy", "commercial_use_terms", "pricing"})
            policies = getattr(obj, "policies", {}) or {}
            pricing = getattr(obj, "pricing", {}) or {}
            if policy_missing or not policies or not pricing:
                return _result(card, "HOLD_POLICY_CLARITY", findings=["Policy, privacy, retention, or pricing metadata is incomplete."], checked=policy_missing or ["policies", "pricing"])
        if card.probe_type == "docs_presence_check" and (not getattr(obj, "docs", {}) or "docs_url" in missing):
            return _result(card, "HOLD_MISSING_FIELDS", findings=["Documentation metadata is incomplete."], checked=["docs"])
        if card.probe_type == "repository_presence_check" and "repository_url" in missing:
            return _result(card, "HOLD_MISSING_FIELDS", findings=["Repository metadata is incomplete."], checked=["repository_url"])
        if card.probe_type == "license_presence_check" and "license" in missing:
            return _result(card, "HOLD_POLICY_CLARITY", findings=["License metadata is incomplete."], checked=["license"])
        return _result(card, "PASS_LOCAL", findings=[f"{card.probe_type} passed on local metadata."])

    if card.probe_type == "unsupported_claim_check":
        claims = [claim for claim in card.forbidden_claims if _contains_positive_phrase(obj_text, claim)]
        if claims:
            return _result(card, "BLOCK_UNSUPPORTED_CLAIM", findings=[f"Unsupported claim wording detected: {', '.join(sorted(claims))}"])
        return _result(card, "PASS_LOCAL", findings=["No unsupported positive claim wording detected in local metadata."])

    if card.probe_type == "forbidden_action_check":
        actions = [action for action in card.forbidden_actions if _contains_positive_phrase(obj_text, action)]
        if actions:
            return _result(card, "BLOCK_FORBIDDEN_ACTION", findings=[f"Forbidden action wording detected: {', '.join(sorted(actions))}"])
        return _result(card, "PASS_LOCAL", findings=["No forbidden action wording detected in local metadata."])

    return _result(card, "INVALID_PROBE", errors=[f"Unsupported probe type: {card.probe_type}"])


def aggregate_probe_results(results: list[ProbeResult]) -> ProbeReceiptAggregate:
    counts = Counter(result.result for result in results)
    return ProbeReceiptAggregate(
        pass_local_count=counts.get("PASS_LOCAL", 0),
        hold_count=sum(count for key, count in counts.items() if key.startswith("HOLD")),
        block_count=sum(count for key, count in counts.items() if key.startswith("BLOCK")),
        fail_unexpected_count=counts.get("FAIL_UNEXPECTED", 0),
        negative_control_pass_count=counts.get("BLOCK_UNSUPPORTED_CLAIM", 0),
        negative_control_fail_count=counts.get("FAIL_EXPECTED_NEGATIVE_CONTROL", 0),
    )


def route_effect_from_results(results: list[ProbeResult]) -> str:
    if any(result.result.startswith("BLOCK") for result in results):
        return "DOWNGRADE_TO_BLOCK"
    if any(result.result.startswith("HOLD") or result.result.startswith("FAIL") for result in results):
        return "DOWNGRADE_TO_HOLD"
    if results:
        return "ADD_WARNING"
    return "NO_CHANGE"


def run_probe_plan(plan: ProbePlan) -> ProbeReceipt:
    results = [run_probe_card(card) for card in plan.probe_cards]
    return ProbeReceipt(
        plan_id=plan.plan_id or "probe-plan-missing",
        probe_results=results,
        aggregate=aggregate_probe_results(results),
        route_effect=route_effect_from_results(results),  # type: ignore[arg-type]
    )
