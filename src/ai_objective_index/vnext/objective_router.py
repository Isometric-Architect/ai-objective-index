from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from ai_objective_index.integrated_store import get_store_for_scope

from .capability_adapter import build_capability_trust_card, objective_request_to_objective_card
from .objective_router_models import ObjectiveRouteRequest, ObjectiveRouteResponse, ObjectiveRouteSummary
from .trust_report import build_capability_trust_report


SUPPORTED_DECISION_LABELS = [
    "ALLOW_CANDIDATE",
    "ALLOW_WITH_LIMITS",
    "HOLD_EVIDENCE",
    "HOLD_MISSING_FIELDS",
    "HOLD_POLICY_CLARITY",
    "HOLD_SECURITY_REVIEW",
    "BLOCK_FORBIDDEN_ACTION",
    "BLOCK_UNSUPPORTED_CLAIM",
    "BLOCK_HIGH_RISK_DOMAIN",
    "BLOCK_NO_SOURCE_TRACE",
]

KNOWN_LIMITS = [
    "Objective Router returns route decisions, not final truth.",
    "ALLOW_CANDIDATE and ALLOW_WITH_LIMITS do not mean verified, safe, security certified, quality guaranteed, or product ready.",
    "HOLD means evidence, policy clarity, or review requirements are insufficient for stronger use.",
    "BLOCK means the route must not be used under the requested scope.",
    "No probes, gateway execution, live URL fetch, external tool execution, or external LLM calls are performed.",
]


def _is_block(decision: str) -> bool:
    return decision.startswith("BLOCK")


def _set_decision(card: dict[str, Any], decision: str, reason: str, next_action: str) -> None:
    current = card.get("route_decision", {})
    if _is_block(str(current.get("decision", ""))):
        return
    current["decision"] = decision
    current["reason"] = reason
    next_actions = list(current.get("next_actions") or [])
    if next_action not in next_actions:
        next_actions.append(next_action)
    current["next_actions"] = next_actions
    current["can_recommend_as_candidate"] = False
    if decision.startswith("HOLD"):
        current["can_rank"] = True
        current["can_compare"] = True
    card["route_decision"] = current


def _constraint_forbidden_detected(card: dict[str, Any], forbidden_actions: list[str]) -> list[str]:
    haystack = " ".join(
        [
            str(card.get("name", "")),
            str(card.get("risk_boundary", {})),
        ]
    ).lower()
    return sorted(action for action in forbidden_actions if action.lower() in haystack)


def _apply_constraints(card: dict[str, Any], request: ObjectiveRouteRequest) -> dict[str, Any]:
    constrained = deepcopy(card)
    constraints = request.constraints
    evidence = constrained.get("evidence_summary", {})
    risk = constrained.get("risk_boundary", {})
    missing = set(constrained.get("missing_fields") or [])
    decision = str(constrained.get("route_decision", {}).get("decision", ""))

    if risk.get("forbidden_actions_detected"):
        constrained["route_decision"]["decision"] = "BLOCK_FORBIDDEN_ACTION"
        constrained["route_decision"]["reason"] = "Forbidden action boundary is present on this candidate."
        constrained["route_decision"]["can_rank"] = False
        constrained["route_decision"]["can_compare"] = False
        constrained["route_decision"]["can_recommend_as_candidate"] = False
        return constrained
    if risk.get("unsupported_claims_detected"):
        constrained["route_decision"]["decision"] = "BLOCK_UNSUPPORTED_CLAIM"
        constrained["route_decision"]["reason"] = "Unsupported verification, safety, certification, or quality claim is present."
        constrained["route_decision"]["can_rank"] = False
        constrained["route_decision"]["can_compare"] = False
        constrained["route_decision"]["can_recommend_as_candidate"] = False
        return constrained
    if evidence.get("source_trace_count", 0) == 0 and constraints.require_source_trace:
        if decision.startswith("ALLOW") or decision.startswith("HOLD"):
            _set_decision(
                constrained,
                "BLOCK_NO_SOURCE_TRACE",
                "Request requires source trace evidence, but this candidate has no source trace.",
                "Add source traces before routing this candidate.",
            )
    if constraints.require_policy_clarity and (
        not evidence.get("policy_found") or {"commercial_use_terms", "privacy_policy", "data_retention_policy"} & missing
    ):
        _set_decision(
            constrained,
            "HOLD_POLICY_CLARITY",
            "Request requires policy clarity, but policy evidence is missing or incomplete.",
            "Collect official policy traces before stronger use.",
        )
    if constraints.require_docs and (not evidence.get("docs_found") or "docs_url" in missing):
        _set_decision(
            constrained,
            "HOLD_MISSING_FIELDS",
            "Request requires documentation evidence, but docs are missing or incomplete.",
            "Add official docs traces before stronger use.",
        )
    if constraints.require_pricing and (not evidence.get("pricing_found") or "pricing" in missing):
        _set_decision(
            constrained,
            "HOLD_MISSING_FIELDS",
            "Request requires pricing evidence, but pricing is missing or incomplete.",
            "Add official pricing traces before stronger use.",
        )
    if constraints.require_license and not evidence.get("license_found"):
        _set_decision(
            constrained,
            "HOLD_POLICY_CLARITY",
            "Request requires license evidence, but license information is missing.",
            "Add official license or terms traces before stronger use.",
        )
    if constraints.require_repository and not evidence.get("repository_found"):
        _set_decision(
            constrained,
            "HOLD_MISSING_FIELDS",
            "Request requires repository evidence, but repository information is missing.",
            "Add official repository trace before stronger use.",
        )
    if constraints.allowed_integration_types and constrained.get("integration_type") not in constraints.allowed_integration_types:
        _set_decision(
            constrained,
            "HOLD_MISSING_FIELDS",
            "Candidate integration type is outside the requested allowed integration types.",
            "Use a candidate whose integration type matches the requested route.",
        )
    if constraints.forbidden_actions:
        detected = _constraint_forbidden_detected(constrained, constraints.forbidden_actions)
        if detected:
            constrained.setdefault("risk_boundary", {}).setdefault("forbidden_actions_detected", [])
            constrained["risk_boundary"]["forbidden_actions_detected"] = sorted(
                set(constrained["risk_boundary"]["forbidden_actions_detected"]) | set(detected)
            )
            constrained["route_decision"]["decision"] = "BLOCK_FORBIDDEN_ACTION"
            constrained["route_decision"]["reason"] = "Requested forbidden action boundary was detected in this route."
            constrained["route_decision"]["can_rank"] = False
            constrained["route_decision"]["can_compare"] = False
            constrained["route_decision"]["can_recommend_as_candidate"] = False
    if constraints.risk_tolerance == "low" and risk.get("risk_level") in {"high", "unknown"}:
        _set_decision(
            constrained,
            "HOLD_SECURITY_REVIEW" if risk.get("risk_level") == "high" else "HOLD_EVIDENCE",
            "Low risk tolerance requires stronger evidence or review before use.",
            "Review risk boundary and evidence before routing under low tolerance.",
        )
    return constrained


def _compact_card(card: dict[str, Any], request: ObjectiveRouteRequest) -> dict[str, Any]:
    compact = deepcopy(card)
    if not request.include.source_traces:
        compact["source_trace_ids"] = []
    if not request.include.missing_fields:
        compact["missing_fields"] = []
    if not request.include.score_components:
        compact["score_components"] = {}
    if not request.include.known_limits:
        compact["known_limits"] = []
    return compact


def _summary(cards: list[dict[str, Any]]) -> ObjectiveRouteSummary:
    counts = Counter(str(card.get("route_decision", {}).get("decision", "UNKNOWN")) for card in cards)
    top_reasons = [
        {
            "decision": card.get("route_decision", {}).get("decision"),
            "reason": card.get("route_decision", {}).get("reason"),
            "name": card.get("name"),
            "object_id": card.get("object_id"),
        }
        for card in cards[:5]
    ]
    return ObjectiveRouteSummary(
        total_candidates=len(cards),
        allow_count=sum(value for key, value in counts.items() if key.startswith("ALLOW")),
        hold_count=sum(value for key, value in counts.items() if key.startswith("HOLD")),
        block_count=sum(value for key, value in counts.items() if key.startswith("BLOCK")),
        top_decision_reasons=top_reasons,
    )


def route_objective(request: ObjectiveRouteRequest) -> ObjectiveRouteResponse:
    report = build_capability_trust_report(
        query=request.query,
        objective=request.objective,
        domain=request.domain,
        data_scope=request.data_scope,
        limit=request.limit,
    )
    cards = [_compact_card(_apply_constraints(card, request), request) for card in report.get("trust_cards", [])]
    next_actions = [
        "Review HOLD and BLOCK reasons before using any route.",
        "Verify source traces against current primary sources for high-stakes use.",
    ]
    if not cards:
        next_actions.append("No candidates were returned; check data_scope or run local data rebuilds.")
    return ObjectiveRouteResponse(
        query=request.query,
        objective=request.objective,
        domain=request.domain,
        data_scope=request.data_scope,
        generated_at=datetime.now(UTC).isoformat(),
        route_summary=_summary(cards),
        results=cards,
        known_limits=KNOWN_LIMITS,
        next_actions=next_actions,
    )


def router_status() -> dict[str, Any]:
    return {
        "schema": "AOI_ObjectiveRouterStatus/v0.1",
        "read_only": True,
        "probe_execution": False,
        "gateway_execution": False,
        "external_fetch": False,
        "external_tool_execution": False,
        "supported_data_scopes": ["sample", "integrated", "mcp_registry", "public_beta_mcp"],
        "supported_decision_labels": SUPPORTED_DECISION_LABELS,
        "claim_boundaries": [
            "not verified",
            "not safe",
            "not security certified",
            "not a quality guarantee",
            "not product ready",
            "not purchasing advice",
        ],
    }


def get_capability_trust(
    capability_id: str,
    data_scope: str = "sample",
    query: str | None = None,
    objective: str | None = None,
    domain: str = "mcp_servers",
) -> dict[str, Any]:
    object_id = capability_id.removeprefix("capability:")
    try:
        store = get_store_for_scope(data_scope)
    except Exception as exc:
        return {
            "read_only": True,
            "found": False,
            "error": "data_scope_unavailable",
            "message": str(exc),
            "capability_id": capability_id,
        }
    action_object = store.get_object(object_id)
    if action_object is None:
        return {
            "read_only": True,
            "found": False,
            "error": "capability_not_found",
            "capability_id": capability_id,
            "data_scope": data_scope,
            "known_limits": KNOWN_LIMITS,
        }
    objective_card = objective_request_to_objective_card(
        query=query or action_object.name,
        objective=objective or "review source-traced capability candidate",
        domain=domain,
    )
    card = build_capability_trust_card(
        action_object=action_object,
        objective_card=objective_card,
        traces=store.get_traces(action_object.object_id),
        query=query or action_object.name,
    )
    return {
        "read_only": True,
        "found": True,
        "data_scope": data_scope,
        "capability_trust_card": card.model_dump(mode="json", by_alias=True),
        "known_limits": KNOWN_LIMITS,
    }


def explain_route_decision(
    capability_id: str,
    objective: str | None = None,
    data_scope: str = "sample",
) -> dict[str, Any]:
    payload = get_capability_trust(capability_id=capability_id, data_scope=data_scope, objective=objective)
    if not payload.get("found"):
        return payload
    card = payload["capability_trust_card"]
    return {
        "read_only": True,
        "capability_id": capability_id,
        "data_scope": data_scope,
        "decision": card["route_decision"]["decision"],
        "reason": card["route_decision"]["reason"],
        "claim_ceiling": card["route_decision"]["claim_ceiling"],
        "evidence_summary": card["evidence_summary"],
        "risk_boundary": card["risk_boundary"],
        "missing_fields": card["missing_fields"],
        "must_not_claim": card["route_decision"]["must_not_claim"],
        "probe_execution": False,
        "gateway_execution": False,
        "external_fetch": False,
    }
