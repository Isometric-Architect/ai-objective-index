from __future__ import annotations

from copy import deepcopy
from typing import Any

from .objective_router import route_objective
from .objective_router_models import ObjectiveRouteRequest
from .probe_card import ProbeCapabilityOverlay, ProbeCard, ProbePlan, ProbeReceipt, ProbeRouteOverlay
from .probe_receipt_store import ProbeReceiptStore
from .probe_runner import run_probe_plan


DEFAULT_ROUTE_PROBES = [
    "source_trace_integrity",
    "policy_clarity_check",
    "missing_field_check",
    "unsupported_claim_check",
    "forbidden_action_check",
]


def _capability_id_for_card(card: dict[str, Any]) -> str:
    return str(card.get("capability_id") or f"capability:{card.get('object_id', '')}")


def _object_id_for_card(card: dict[str, Any]) -> str | None:
    value = card.get("object_id")
    return str(value) if value else None


def build_probe_plan_for_route(route_response: dict[str, Any], route_request: dict[str, Any] | None = None) -> ProbePlan:
    probe_cards: list[ProbeCard] = []
    objective_id = None
    if route_request:
        objective_id = str(route_request.get("objective_id") or route_request.get("objective") or "") or None
    data_scope = str(route_response.get("data_scope") or (route_request or {}).get("data_scope") or "sample")
    for card in route_response.get("results", []):
        capability_id = _capability_id_for_card(card)
        object_id = _object_id_for_card(card)
        name = str(card.get("name") or capability_id)
        for probe_type in DEFAULT_ROUTE_PROBES:
            required_fields = []
            if probe_type == "policy_clarity_check":
                required_fields = ["privacy_policy", "data_retention_policy", "commercial_use_terms", "pricing"]
            if probe_type == "missing_field_check":
                required_fields = list(card.get("missing_fields") or [])[:8]
            probe_cards.append(
                ProbeCard(
                    probe_type=probe_type,  # type: ignore[arg-type]
                    objective_id=objective_id,
                    capability_id=capability_id,
                    object_id=object_id,
                    name=name,
                    data_scope=data_scope,
                    probe_goal=f"Run {probe_type} before using this capability route.",
                    required_fields=required_fields,
                )
            )
    return ProbePlan(
        objective_id=objective_id,
        route_request=route_request or {},
        capability_ids=sorted({_capability_id_for_card(card) for card in route_response.get("results", [])}),
        probe_cards=probe_cards,
        plan_scope="local_metadata_only",
    )


def run_local_probes_for_route(route_response: dict[str, Any], route_request: dict[str, Any] | None = None) -> ProbeReceipt:
    return run_probe_plan(build_probe_plan_for_route(route_response, route_request=route_request))


def _effect_for_capability(capability_id: str, results: list[str], current_decision: str) -> ProbeCapabilityOverlay:
    notes: list[str] = []
    effect = "NO_CHANGE"
    if any(result.startswith("BLOCK") for result in results):
        effect = "DOWNGRADE_TO_BLOCK"
        notes.append("Local metadata probe found a block signal.")
    elif any(result.startswith("HOLD") or result.startswith("FAIL") for result in results):
        if current_decision.startswith("ALLOW"):
            effect = "DOWNGRADE_TO_HOLD"
            notes.append("Local metadata probe added a hold signal.")
        else:
            effect = "ADD_WARNING"
            notes.append("Local metadata probe keeps the route conservative.")
    elif current_decision.startswith("HOLD"):
        effect = "DO_NOT_UPGRADE"
        notes.append("Local probe pass does not upgrade HOLD to ALLOW in this MVP.")
    elif results:
        effect = "ADD_WARNING"
        notes.append("Local probe pass is not verification or action authorization.")
    return ProbeCapabilityOverlay(
        capability_id=capability_id,
        probe_results=results,
        overlay_notes=notes,
        decision_effect=effect,  # type: ignore[arg-type]
    )


def overlay_probe_results(
    route_response: dict[str, Any],
    probe_receipt: ProbeReceipt | dict[str, Any] | None,
    route_request: dict[str, Any] | None = None,
) -> ProbeRouteOverlay:
    receipt_payload = (
        probe_receipt.model_dump(mode="json", by_alias=True)
        if hasattr(probe_receipt, "model_dump")
        else (probe_receipt or {})
    )
    results_by_capability: dict[str, list[str]] = {}
    for item in receipt_payload.get("probe_results", []):
        results_by_capability.setdefault(str(item.get("capability_id")), []).append(str(item.get("result")))
    overlays = []
    for card in route_response.get("results", []):
        capability_id = _capability_id_for_card(card)
        decision = str(card.get("route_decision", {}).get("decision", ""))
        overlays.append(_effect_for_capability(capability_id, results_by_capability.get(capability_id, []), decision))
    return ProbeRouteOverlay(
        route_request=route_request or {},
        original_route_summary=route_response.get("route_summary", {}),
        probe_plan_id=receipt_payload.get("plan_id"),
        probe_receipt_id=receipt_payload.get("receipt_id"),
        probe_memory_applied=bool(receipt_payload.get("probe_results")),
        per_capability_probe_overlay=overlays,
    )


def _apply_probe_overlay_to_card(card: dict[str, Any], overlay: ProbeCapabilityOverlay) -> dict[str, Any]:
    updated = deepcopy(card)
    route_decision = updated.setdefault("route_decision", {})
    next_actions = route_decision.setdefault("next_actions", [])
    for note in overlay.overlay_notes:
        if note not in next_actions:
            next_actions.append(note)
    current = str(route_decision.get("decision", ""))
    if overlay.decision_effect == "DOWNGRADE_TO_BLOCK":
        route_decision["decision"] = "BLOCK_UNSUPPORTED_CLAIM"
        route_decision["reason"] = "Local probe overlay produced a block signal."
        route_decision["can_rank"] = False
        route_decision["can_compare"] = False
        route_decision["can_recommend_as_candidate"] = False
    elif overlay.decision_effect == "DOWNGRADE_TO_HOLD" and current.startswith("ALLOW"):
        route_decision["decision"] = "HOLD_EVIDENCE"
        route_decision["reason"] = "Local probe overlay produced a hold signal."
        route_decision["can_recommend_as_candidate"] = False
    updated["route_decision"] = route_decision
    return updated


def route_objective_with_probes(
    request: ObjectiveRouteRequest,
    run_local_probes: bool = False,
    store: ProbeReceiptStore | None = None,
) -> dict[str, Any]:
    route_payload = route_objective(request).model_dump(mode="json", by_alias=True)
    receipt: ProbeReceipt | None = None
    if run_local_probes:
        receipt = run_local_probes_for_route(route_payload, route_request=request.model_dump(mode="json"))
        if store is not None:
            store.append_probe_receipt(receipt)
    overlay = overlay_probe_results(route_payload, receipt, route_request=request.model_dump(mode="json"))
    overlay_by_id = {item.capability_id: item for item in overlay.per_capability_probe_overlay}
    route_payload["results"] = [
        _apply_probe_overlay_to_card(card, overlay_by_id.get(_capability_id_for_card(card), ProbeCapabilityOverlay(capability_id=_capability_id_for_card(card))))
        for card in route_payload.get("results", [])
    ]
    route_payload["probe_route_overlay"] = overlay.model_dump(mode="json", by_alias=True)
    route_payload["known_limits"] = list(route_payload.get("known_limits", [])) + [
        "Local probes can warn or downgrade routes; they cannot verify, certify, or authorize action.",
        "No live MCP call, external tool execution, URL fetch, crawler, or gateway execution is performed.",
    ]
    route_payload["local_probe_only"] = True
    route_payload["network_used"] = False
    route_payload["external_tool_execution"] = False
    route_payload["gateway_execution"] = False
    return route_payload
