from __future__ import annotations

from typing import Any

from .capability_decision_packet import build_capability_decision_packet


def attach_discover_cdp(response: dict[str, Any]) -> dict[str, Any]:
    candidate = response.get("best_current_candidate") or (response.get("top_candidates") or [{}])[0]
    packet = build_capability_decision_packet(
        objective=str(response.get("objective", "")),
        capability_id=str(candidate.get("candidate_id", "unknown-candidate")),
        capability_name=str(candidate.get("name", "Unknown candidate")),
        capability_type=str(candidate.get("capability_type", "mcp_or_api")),
        source_trace_refs=list(candidate.get("source_trace_refs", [])),
        missing_fields=list(candidate.get("missing_fields", [])),
        route_decision="HOLD_MISSING_FIELDS",
    )
    response["capability_decision_packet"] = packet
    return response


def attach_preflight_cdp(response: dict[str, Any]) -> dict[str, Any]:
    packet = build_capability_decision_packet(
        objective=str(response.get("objective") or response.get("intended_use") or ""),
        capability_id=str(response.get("candidate_id", "unknown-candidate")),
        capability_name=str(response.get("candidate_id", "Unknown candidate")),
        missing_fields=list(response.get("missing_fields", [])),
        route_decision=_normalize_preflight_route(str(response.get("route_decision", "HOLD_MISSING_FIELDS"))),
        safe_next_action=str(response.get("next_action", "")) or None,
    )
    response["capability_decision_packet"] = packet
    return response


def _normalize_preflight_route(route: str) -> str:
    return {
        "HOLD_MISSING_PERMISSION_SCOPE": "HOLD_AUTHORIZATION",
        "BLOCK_EXTERNAL_ACTION": "BLOCK_ACTION_AUTHORIZATION_CLAIM",
    }.get(route, route if route else "HOLD_MISSING_FIELDS")
