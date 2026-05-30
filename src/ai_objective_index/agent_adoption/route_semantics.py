from __future__ import annotations


DISCOVERY_ROUTES = [
    "FOUND_ONLY",
    "SCHEMA_READABLE",
    "SOURCE_TRACED",
    "METADATA_PARTIAL",
    "METADATA_COMPLETE_ENOUGH",
]

ALLOW_ROUTES = [
    "ALLOW_DISCOVERY_ONLY",
    "ALLOW_READ_ONLY",
    "ALLOW_DRAFT_ONLY",
    "ALLOW_LOW_RISK_CALL",
]

HOLD_ROUTES = [
    "HOLD_MISSING_FIELDS",
    "HOLD_AUTHORIZATION",
    "HOLD_SECURITY_REVIEW",
    "HOLD_PRIVACY_REVIEW",
    "HOLD_POLICY_CLARITY",
    "HOLD_STALE_METADATA",
    "HOLD_RUGPULL_DIFF",
    "HOLD_RATE_LIMIT_OR_COST",
    "HOLD_CONTEXT_AMBIGUITY",
]

BLOCK_ROUTES = [
    "BLOCK_UNTRUSTED_SOURCE",
    "BLOCK_DESTRUCTIVE_ACTION",
    "BLOCK_SECRET_OR_PRIVATE_DATA",
    "BLOCK_CERTIFICATION_CLAIM",
    "BLOCK_PRODUCT_READINESS_CLAIM",
    "BLOCK_ACTION_AUTHORIZATION_CLAIM",
    "BLOCK_POLICY_FORBIDDEN",
]

ESCALATE_ROUTES = [
    "ESCALATE_AGENTSEC",
    "ESCALATE_QIRA",
    "ESCALATE_DATACAPSULE",
    "ESCALATE_HUMAN_APPROVAL",
    "ESCALATE_OPERATOR_POLICY",
]

ROUTE_CLASSES = DISCOVERY_ROUTES + ALLOW_ROUTES + HOLD_ROUTES + BLOCK_ROUTES + ESCALATE_ROUTES

EXPLICIT_SEPARATIONS = [
    "FOUND != TRUSTED",
    "TRUSTED != AUTHORIZED",
    "AUTHORIZED != EXECUTABLE",
    "SCHEMA_READABLE != ACTION_ALLOWED",
    "REGISTRY_LISTED != APPROVED",
    "SOURCE_TRACED != SECURITY_CERTIFIED",
    "METADATA_COMPLETE != SAFE_TO_EXECUTE",
    "ALLOW_DISCOVERY_ONLY != ALLOW_EXECUTION",
    "ALLOW_READ_ONLY != ALLOW_WRITE",
    "ALLOW_DRAFT_ONLY != ALLOW_SEND",
]


def route_family(route: str) -> str:
    if route in DISCOVERY_ROUTES:
        return "discovery"
    if route in ALLOW_ROUTES:
        return "allow"
    if route in HOLD_ROUTES:
        return "hold"
    if route in BLOCK_ROUTES:
        return "block"
    if route in ESCALATE_ROUTES:
        return "escalate"
    return "unknown"


def is_route_class(route: str) -> bool:
    return route in ROUTE_CLASSES


def is_execution_authorizing_route(route: str) -> bool:
    return route == "ALLOW_LOW_RISK_CALL"


def route_requires_next_action(route: str) -> bool:
    return route in HOLD_ROUTES


def route_requires_reason_codes(route: str) -> bool:
    return route in BLOCK_ROUTES or route in ESCALATE_ROUTES


def escalation_target_for_route(route: str) -> str:
    return {
        "ESCALATE_AGENTSEC": "AgentSec",
        "ESCALATE_QIRA": "QIRA",
        "ESCALATE_DATACAPSULE": "DataCapsule",
        "ESCALATE_HUMAN_APPROVAL": "HumanApproval",
        "ESCALATE_OPERATOR_POLICY": "OperatorPolicy",
        "HOLD_SECURITY_REVIEW": "AgentSec",
        "HOLD_PRIVACY_REVIEW": "DataCapsule",
        "HOLD_POLICY_CLARITY": "OperatorPolicy",
        "HOLD_RUGPULL_DIFF": "AgentSec",
    }.get(route, "")


def separation_claims() -> dict[str, bool]:
    return {
        "found_is_trusted": False,
        "trusted_is_authorized": False,
        "authorized_is_executable": False,
        "schema_readable_is_action_allowed": False,
        "registry_listed_is_approved": False,
        "source_traced_is_security_certified": False,
        "metadata_complete_is_safe_to_execute": False,
        "allow_discovery_only_is_execution": False,
        "allow_read_only_is_write": False,
        "allow_draft_only_is_send": False,
    }
