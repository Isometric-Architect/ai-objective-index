from __future__ import annotations

from typing import Any

from . import timestamp
from .agent_claim_boundary import CLAIM_BOUNDARY, MUST_NOT_CLAIM
from .freshness_policy import freshness_fields
from .route_reason_codes import reason_codes_for_route
from .route_semantics import escalation_target_for_route, route_family


SCHEMA_VERSION = "AOI_CapabilityDecisionPacket/v0.1"

REQUIRED_FIELDS = [
    "schema_version",
    "packet_id",
    "objective",
    "capability_id",
    "capability_name",
    "candidate_source",
    "capability_type",
    "objective_fit_score",
    "source_trace_status",
    "source_trace_refs",
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
    "discovered_state",
    "trusted_state",
    "authorized_state",
    "executable_state",
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
    "claim_ceiling",
]


def build_capability_decision_packet(
    *,
    objective: str,
    capability_id: str,
    capability_name: str,
    candidate_source: str = "local_agent_discovery_sample",
    capability_type: str = "mcp_or_api",
    objective_fit_score: float = 0.72,
    source_trace_refs: list[str] | None = None,
    missing_fields: list[str] | None = None,
    route_decision: str = "HOLD_MISSING_FIELDS",
    safe_next_action: str | None = None,
    blocked_next_actions: list[str] | None = None,
    action_level: str = "read_or_draft_only",
    data_boundary: str = "metadata_only",
    current_auth_context_known: bool = False,
    stale: bool = True,
    rugpull_diff_status: str = "not_checked",
    known_negative_cache_hit: bool = False,
) -> dict[str, Any]:
    traces = source_trace_refs or ["README.md", "docs/aoi_agent_native_discovery.md"]
    missing = missing_fields or ["permission_scope", "freshness_recheck"]
    freshness = freshness_fields(stale=stale, rugpull_status=rugpull_diff_status, negative_cache_hit=known_negative_cache_hit)
    route_reasons = reason_codes_for_route(route_decision)
    family = route_family(route_decision)
    escalation = escalation_target_for_route(route_decision)
    if family == "escalate" and not escalation:
        escalation = "HumanApproval"
    if not safe_next_action:
        safe_next_action = _default_safe_next_action(route_decision)
    blocked = blocked_next_actions or [
        "external tool execution",
        "write/send/delete action",
        "certification or product-readiness claim",
        "action authorization claim",
    ]

    packet = {
        "schema_version": SCHEMA_VERSION,
        "packet_id": f"cdp-{capability_id}",
        "objective": objective,
        "capability_id": capability_id,
        "capability_name": capability_name,
        "candidate_source": candidate_source,
        "capability_type": capability_type,
        "objective_fit_score": objective_fit_score,
        "source_trace_status": "source_traced" if traces else "source_trace_missing",
        "source_trace_refs": traces,
        "metadata_completeness": "partial" if missing else "complete_enough_for_route",
        "action_level": action_level,
        "data_boundary": data_boundary,
        "auth_scope_required": "explicit_permission_scope_required",
        "current_auth_context_known": current_auth_context_known,
        "discovered_state": "discovered" if traces else "found_untraced",
        "trusted_state": "not_verified",
        "authorized_state": "not_authorized",
        "executable_state": "not_executable",
        "route_decision": route_decision,
        "route_reason_codes": route_reasons,
        "missing_fields": missing,
        "safe_next_action": safe_next_action,
        "blocked_next_actions": blocked,
        "escalation_path": escalation,
        "must_not_claim": MUST_NOT_CLAIM,
        "receipt_id": f"receipt-{capability_id}-{route_decision.lower()}",
        "decision_timestamp": timestamp(),
        "claim_ceiling": CLAIM_BOUNDARY
        + [
            "objective_fit_score does not imply safety",
            "metadata_completeness does not imply authorization",
            "route_decision does not imply security certification",
            "route_decision does not imply product readiness",
            "route_decision does not imply action authorization",
        ],
        "external_action_authorization": False,
        "security_certification": False,
        "product_readiness_claim": False,
        "private_kernel_exposed": False,
    }
    packet.update(freshness)
    return packet


def _default_safe_next_action(route_decision: str) -> str:
    if route_decision.startswith("HOLD"):
        return "Request missing evidence, downgrade to read/draft, or use HOLD-to-Replan before any execution."
    if route_decision.startswith("BLOCK"):
        return "Stop the proposed action and remove the blocked condition before re-evaluation."
    if route_decision.startswith("ESCALATE"):
        return "Send the local packet to the named escalation path; do not execute external action."
    if route_decision == "ALLOW_DISCOVERY_ONLY":
        return "Use for candidate comparison only; do not execute."
    if route_decision == "ALLOW_READ_ONLY":
        return "Proceed with read-only review only."
    if route_decision == "ALLOW_DRAFT_ONLY":
        return "Draft locally without sending or mutating anything."
    return "Proceed only within the stated route and claim ceiling."


def validate_capability_decision_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in packet:
            errors.append(f"missing:{field}")
    route = str(packet.get("route_decision", ""))
    if route.startswith("HOLD") and not (packet.get("safe_next_action") or packet.get("escalation_path")):
        errors.append("hold_missing_next_action")
    if route.startswith("BLOCK") and not packet.get("route_reason_codes"):
        errors.append("block_missing_reason_codes")
    if route.startswith("ESCALATE") and not packet.get("escalation_path"):
        errors.append("escalate_missing_target")
    if packet.get("security_certification") is not False:
        errors.append("security_certification_overclaim")
    if packet.get("product_readiness_claim") is not False:
        errors.append("product_readiness_overclaim")
    if packet.get("external_action_authorization") is not False:
        errors.append("action_authorization_overclaim")
    if packet.get("private_kernel_exposed") is not False:
        errors.append("private_kernel_exposed")
    return errors


def sample_capability_decision_packet() -> dict[str, Any]:
    return build_capability_decision_packet(
        objective="Find a source-traced read-only MCP/API capability candidate.",
        capability_id="aoi-read-only-mcp-tools",
        capability_name="AI Objective Index read-only MCP tools",
        route_decision="HOLD_MISSING_FIELDS",
    )
