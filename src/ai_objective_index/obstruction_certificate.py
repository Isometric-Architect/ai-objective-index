from __future__ import annotations

from collections import Counter
from enum import Enum
from typing import Any

from .action_boundary import check_action_boundary
from .claim_ceiling import ClaimCeiling, infer_claim_ceiling
from .missing_fields import list_missing_fields
from .models import ActionObject, ObstructionCertificate, SourceTrace


class ObstructionToken(str, Enum):
    HOLD_SOURCE = "HOLD_SOURCE"
    HOLD_POLICY = "HOLD_POLICY"
    HOLD_PRICE = "HOLD_PRICE"
    HOLD_FRESHNESS = "HOLD_FRESHNESS"
    HOLD_VALIDATOR = "HOLD_VALIDATOR"
    HOLD_USE_RIGHT = "HOLD_USE_RIGHT"
    HOLD_ACTION_BOUNDARY = "HOLD_ACTION_BOUNDARY"
    BLOCK_UNSAFE_CLAIM = "BLOCK_UNSAFE_CLAIM"
    BLOCK_FORBIDDEN_ACTION = "BLOCK_FORBIDDEN_ACTION"
    BLOCK_FORBIDDEN_PROMOTION = "BLOCK_FORBIDDEN_PROMOTION"


def _trace_ids(traces: list[SourceTrace] | None) -> list[str]:
    return [trace.trace_id for trace in traces or []]


def _cert(
    action_object: ActionObject,
    token: ObstructionToken,
    reason: str,
    missing_evidence: list[str],
    next_action: str,
    severity: str,
    traces: list[SourceTrace] | None,
) -> ObstructionCertificate:
    return ObstructionCertificate(
        object_id=action_object.object_id,
        token=token.value,
        reason=reason,
        missing_evidence=missing_evidence,
        next_action=next_action,
        severity=severity,  # type: ignore[arg-type]
        source_trace_ids=_trace_ids(traces),
    )


def build_obstructions(
    action_object: ActionObject,
    traces: list[SourceTrace] | None = None,
    requested_action: str | None = None,
) -> list[ObstructionCertificate]:
    obstructions: list[ObstructionCertificate] = []
    missing_names = {item.field for item in list_missing_fields(action_object)}

    if "pricing" in missing_names or "free_plan" in missing_names:
        obstructions.append(
            _cert(
                action_object,
                ObstructionToken.HOLD_PRICE,
                "Pricing or free-plan evidence is missing or weak.",
                sorted(missing_names & {"pricing", "free_plan", "rate_limits"}),
                "Find an official pricing or billing limits source before making price-clear claims.",
                "high",
                traces,
            )
        )
    if missing_names & {"commercial_use_terms", "privacy_policy", "data_retention_policy", "license"}:
        obstructions.append(
            _cert(
                action_object,
                ObstructionToken.HOLD_POLICY,
                "Policy or commercial-use evidence is missing or weak.",
                sorted(missing_names & {"commercial_use_terms", "privacy_policy", "data_retention_policy", "license"}),
                "Find official terms, privacy, retention, license, or commercial-use pages before promoting policy claims.",
                "high",
                traces,
            )
        )
    if not traces:
        obstructions.append(
            _cert(
                action_object,
                ObstructionToken.HOLD_SOURCE,
                "No source traces are attached for this object in the current run.",
                ["source_trace"],
                "Attach field-level source traces before treating extracted fields as source-traced readouts.",
                "medium",
                traces,
            )
        )

    status = str(action_object.status.value if hasattr(action_object.status, "value") else action_object.status).upper()
    if status == "STALE":
        obstructions.append(
            _cert(
                action_object,
                ObstructionToken.HOLD_FRESHNESS,
                "The object is stale and cannot be presented as current truth.",
                ["freshness_reconfirmation"],
                "Reconfirm official sources and update retrieval timestamps.",
                "high",
                traces,
            )
        )
    if status == "BLOCKED":
        obstructions.append(
            _cert(
                action_object,
                ObstructionToken.BLOCK_UNSAFE_CLAIM,
                "The object is blocked from promotion.",
                ["safe_claim_review"],
                "Remove unsafe claim paths or keep the object blocked.",
                "block",
                traces,
            )
        )

    ceiling = infer_claim_ceiling(action_object, traces)
    if ceiling in {ClaimCeiling.EXTRACTED_UNVERIFIED, ClaimCeiling.SAMPLE_BENCHMARK_ONLY}:
        obstructions.append(
            _cert(
                action_object,
                ObstructionToken.HOLD_VALIDATOR,
                "The claim ceiling prevents verified-object promotion.",
                ["validator_review"],
                "Keep as sample/extracted readout or add an explicit future validator workflow.",
                "medium",
                traces,
            )
        )

    if requested_action:
        boundary = check_action_boundary(requested_action)
        if boundary["decision"] == "BLOCK":
            obstructions.append(
                _cert(
                    action_object,
                    ObstructionToken.BLOCK_FORBIDDEN_ACTION,
                    boundary["reason"],
                    [requested_action],
                    "Use only AOI read-only actions: read, rank, compare, explain, quote snippet, or decision receipt.",
                    "block",
                    traces,
                )
            )
        elif boundary["decision"] == "HOLD":
            obstructions.append(
                _cert(
                    action_object,
                    ObstructionToken.HOLD_ACTION_BOUNDARY,
                    boundary["reason"],
                    [requested_action],
                    "Review the requested action against the AOI action boundary before proceeding.",
                    "high",
                    traces,
                )
            )
    return obstructions


def summarize_obstructions(obstructions: list[ObstructionCertificate]) -> dict[str, Any]:
    tokens = Counter(item.token for item in obstructions)
    severities = Counter(item.severity for item in obstructions)
    return {
        "count": len(obstructions),
        "tokens": dict(tokens),
        "severities": dict(severities),
        "has_block": any(item.severity == "block" for item in obstructions),
        "hold_next_actions": [item.next_action for item in obstructions if item.token.startswith("HOLD_")],
    }
