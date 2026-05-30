from __future__ import annotations

from typing import Any

from .route_semantics import is_execution_authorizing_route, route_family


def validate_state_separation(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if packet.get("discovered_state") == "discovered" and packet.get("trusted_state") == "trusted":
        errors.append("discovered_cannot_imply_trusted")
    if packet.get("trusted_state") == "trusted" and packet.get("authorized_state") == "authorized":
        errors.append("trusted_cannot_imply_authorized")
    if packet.get("authorized_state") == "authorized" and packet.get("executable_state") == "executable":
        errors.append("authorized_cannot_imply_executable")
    return errors


def allowed_action_for_route(route: str) -> dict[str, Any]:
    return {
        "route_decision": route,
        "route_family": route_family(route),
        "allows_discovery": route in {"ALLOW_DISCOVERY_ONLY", "ALLOW_READ_ONLY", "ALLOW_DRAFT_ONLY", "ALLOW_LOW_RISK_CALL"},
        "allows_read": route in {"ALLOW_READ_ONLY", "ALLOW_DRAFT_ONLY", "ALLOW_LOW_RISK_CALL"},
        "allows_draft": route in {"ALLOW_DRAFT_ONLY", "ALLOW_LOW_RISK_CALL"},
        "allows_execution": is_execution_authorizing_route(route),
        "allows_write": False,
        "allows_send": False,
        "allows_delete": False,
        "action_authorization": False,
    }


def transition_allowed(current_route: str, requested_route: str, new_evidence_attached: bool = False) -> bool:
    if current_route.startswith("BLOCK"):
        return False
    if current_route.startswith("HOLD") and requested_route.startswith("ALLOW"):
        return new_evidence_attached
    if current_route == "ALLOW_DISCOVERY_ONLY" and requested_route == "ALLOW_LOW_RISK_CALL":
        return new_evidence_attached
    return True
