from __future__ import annotations

from typing import Any


FEEDBACK_PACKET_SCHEMA = "AOI_ExternalModelFeedbackPacket/v0.1"
CROSS_MODEL_SUMMARY_SCHEMA = "AOI_CrossModelFeedbackSummary/v0.1"
ROUTE_SEMANTICS_ROADMAP_SCHEMA = "AOI_RouteSemanticsRoadmap/v0.1"
TEST_RESIDUAL_RECONCILIATION_SCHEMA = "AOI_TestResidualReconciliation/v0.1"

FEEDBACK_CATEGORIES = [
    "DISCOVERY_FAST_PATH",
    "PREFLIGHT_TRUST_ROUTER",
    "CAPABILITY_DECISION_PACKET",
    "ROUTE_LABEL_GRANULARITY",
    "HOLD_TO_REPLAN_LOOP",
    "ADAPTIVE_GOVERNANCE",
    "CONTEXT_AWARE_POLICY",
    "FRESHNESS_STALENESS",
    "RUGPULL_DIFF",
    "NEGATIVE_CACHE",
    "LATENCY_BUDGET",
    "AGENT_OPERATOR_POSITIONING",
    "NON_BYPASSABLE_MIDDLEWARE",
    "ENTERPRISE_ESCALATION",
    "CLAIM_BOUNDARY",
    "PRIVATE_KERNEL_PROTECTION",
    "INCUMBENT_COMPETITION",
    "DATA_FRAGMENTATION",
    "TRUST_ROUTER_TRUST_REGRESSION",
]

PACKET_REQUIRED_FIELDS = [
    "schema",
    "model_name",
    "prompt_set",
    "key_positive_findings",
    "key_adoption_blockers",
    "recommended_killer_features",
    "route_semantics_recommendations",
    "freshness_or_rugpull_recommendations",
    "enterprise_or_operator_positioning",
    "claim_boundary_warnings",
    "overclaim_risks",
    "direct_quotes_short_safe_only",
    "redaction_status",
]


def validate_feedback_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in PACKET_REQUIRED_FIELDS:
        if field not in packet:
            errors.append(f"missing:{field}")
    if packet.get("schema") != FEEDBACK_PACKET_SCHEMA:
        errors.append("schema_mismatch")
    if packet.get("redaction_status") != "PASS_REDACTED":
        errors.append("redaction_not_pass")
    if packet.get("external_llm_api_called") is not False:
        errors.append("external_llm_api_called_not_false")
    if packet.get("private_kernel_exposed") is not False:
        errors.append("private_kernel_exposed_not_false")
    return errors


def route_classes() -> list[str]:
    return [
        "FOUND_ONLY",
        "SCHEMA_READABLE",
        "ALLOW_DISCOVERY_ONLY",
        "ALLOW_READ_ONLY",
        "ALLOW_DRAFT_ONLY",
        "ALLOW_LOW_RISK_CALL",
        "HOLD_MISSING_FIELDS",
        "HOLD_AUTHORIZATION",
        "HOLD_SECURITY_REVIEW",
        "HOLD_PRIVACY_REVIEW",
        "HOLD_POLICY_CLARITY",
        "HOLD_STALE_METADATA",
        "HOLD_RUGPULL_DIFF",
        "BLOCK_UNTRUSTED_SOURCE",
        "BLOCK_DESTRUCTIVE_ACTION",
        "BLOCK_SECRET_OR_PRIVATE_DATA",
        "BLOCK_CERTIFICATION_CLAIM",
        "ESCALATE_AGENTSEC",
        "ESCALATE_QIRA",
        "ESCALATE_DATACAPSULE",
        "ESCALATE_HUMAN_APPROVAL",
    ]


def capability_decision_packet_fields() -> list[str]:
    return [
        "objective",
        "capability_id",
        "candidate_source",
        "capability_type",
        "objective_fit_score",
        "source_trace_status",
        "metadata_completeness",
        "freshness_status",
        "version_pin",
        "last_checked_at",
        "stale_warning",
        "rugpull_diff_status",
        "known_negative_cache_hit",
        "action_level",
        "data_boundary",
        "auth_scope_required",
        "current_auth_context_known",
        "route_decision",
        "route_reason_codes",
        "missing_fields",
        "safe_next_action",
        "blocked_next_actions",
        "escalation_path",
        "must_not_claim",
        "receipt_id",
        "decision_timestamp",
        "recheck_policy",
    ]
