from __future__ import annotations

from typing import Any

from ai_objective_index.models import ActionObject, SourceTrace

from .mcp_registry_evidence_gate import validate_registry_dataset
from .mcp_registry_loader import detect_registry_payload_shape, normalize_registry_records


def _status(action_object: ActionObject) -> str:
    return str(action_object.status.value if hasattr(action_object.status, "value") else action_object.status).upper()


def validate_live_payload_shape(raw: Any, max_servers: int = 50) -> dict[str, Any]:
    shape = detect_registry_payload_shape(raw)
    records = normalize_registry_records(raw)
    warnings: list[str] = []
    errors: list[str] = []
    if shape["record_count"] == 0:
        errors.append("No registry server records found in servers/items/list/data payload shape.")
    if len(records) > max_servers:
        warnings.append(f"object count {len(records)} exceeds max_servers {max_servers}")
    return {
        **shape,
        "max_servers": max_servers,
        "within_max_servers": len(records) <= max_servers,
        "errors": errors,
        "warnings": warnings,
    }


def validate_live_objects(
    objects: list[ActionObject],
    traces: list[SourceTrace],
    max_servers: int = 50,
    live_network_used: bool = False,
    arbitrary_scraping_used: bool = False,
    link_following_used: bool = False,
) -> dict[str, Any]:
    validation = validate_registry_dataset(objects, traces)
    statuses = [_status(item) for item in objects]
    errors: list[str] = []
    warnings: list[str] = []
    if len(objects) > max_servers:
        errors.append(f"object count {len(objects)} exceeds max_servers {max_servers}")
    if any(status in {"VERIFIED", "ACTION_READY"} for status in statuses):
        errors.append("Registry objects must not be VERIFIED or ACTION_READY.")
    if objects and not traces:
        errors.append("Registry objects require source traces.")
    if arbitrary_scraping_used:
        errors.append("Arbitrary scraping must remain false.")
    if link_following_used:
        errors.append("Link following must remain false.")
    return {
        "object_count": len(objects),
        "trace_count": len(traces),
        "max_servers": max_servers,
        "within_max_servers": len(objects) <= max_servers,
        "live_network_used": live_network_used,
        "arbitrary_scraping_used": arbitrary_scraping_used,
        "link_following_used": link_following_used,
        "no_forbidden_status": not any(status in {"VERIFIED", "ACTION_READY"} for status in statuses),
        "traces_exist": bool(traces) or not objects,
        "evidence_gate": validation,
        "errors": errors,
        "warnings": warnings,
    }


def summarize_live_registry_run(
    mode: str,
    payload_validation: dict[str, Any],
    object_validation: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    return {
        "mode": mode,
        "payload_shape": payload_validation.get("shape"),
        "object_count": object_validation.get("object_count", 0),
        "trace_count": object_validation.get("trace_count", 0),
        "public_beta_ready_count": receipt.get("public_beta_ready_count", 0),
        "live_network_used": receipt.get("live_network_used", False),
        "arbitrary_scraping_used": receipt.get("arbitrary_scraping_used", False),
        "link_following_used": receipt.get("link_following_used", False),
        "credentials_used": receipt.get("credentials_used", False),
        "errors": [*payload_validation.get("errors", []), *object_validation.get("errors", []), *receipt.get("errors", [])],
        "warnings": [*payload_validation.get("warnings", []), *object_validation.get("warnings", []), *receipt.get("warnings", [])],
    }

