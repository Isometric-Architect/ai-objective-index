from __future__ import annotations

from copy import deepcopy
from typing import Any

from .execution_receipt_loop import ReceiptCapabilityOverlay, ReceiptRouteOverlay
from .execution_receipt_store import ExecutionReceiptStore
from .objective_router import route_objective
from .objective_router_models import ObjectiveRouteRequest


def _capability_id_for_card(card: dict[str, Any]) -> str:
    return str(card.get("capability_id") or f"capability:{card.get('object_id', '')}")


def _effect_from_memory(card: dict[str, Any], memory: dict[str, Any]) -> ReceiptCapabilityOverlay:
    capability_id = _capability_id_for_card(card)
    count = int(memory.get("receipt_count", 0))
    if count == 0:
        return ReceiptCapabilityOverlay(capability_id=capability_id, receipt_count=0)
    outcome_counts = memory.get("outcome_counts", {})
    decision = str(card.get("route_decision", {}).get("decision", ""))
    failures = int(outcome_counts.get("fail", 0)) + int(outcome_counts.get("blocked", 0))
    notes: list[str] = []
    effect = "ADD_WARNING"
    failure_signal = "none"
    outcome_signal = ", ".join(f"{key}:{value}" for key, value in sorted(outcome_counts.items()))
    if failures:
        failure_signal = "failure_receipts_present"
        notes.append("Local receipt memory contains failure or blocked outcomes.")
        if decision.startswith("ALLOW"):
            effect = "DOWNGRADE_TO_HOLD"
        elif decision.startswith("HOLD"):
            effect = "ADD_WARNING"
        elif decision.startswith("BLOCK"):
            effect = "NO_CHANGE"
    elif decision.startswith("HOLD"):
        effect = "DO_NOT_UPGRADE"
        notes.append("Receipt memory is present, but this MVP does not upgrade HOLD routes to ALLOW.")
    else:
        notes.append("Receipt memory adds context only; it is not verification.")
    for failure in memory.get("known_failures", [])[:3]:
        notes.append(f"Known failure: {failure}")
    return ReceiptCapabilityOverlay(
        capability_id=capability_id,
        receipt_count=count,
        outcome_signal=outcome_signal or "receipts_available",
        failure_signal=failure_signal,
        overlay_notes=notes,
        decision_effect=effect,  # type: ignore[arg-type]
    )


def _apply_overlay_to_card(card: dict[str, Any], overlay: ReceiptCapabilityOverlay) -> dict[str, Any]:
    updated = deepcopy(card)
    route_decision = updated.setdefault("route_decision", {})
    notes = route_decision.setdefault("next_actions", [])
    for note in overlay.overlay_notes:
        if note not in notes:
            notes.append(note)
    if overlay.decision_effect == "DOWNGRADE_TO_HOLD" and str(route_decision.get("decision", "")).startswith("ALLOW"):
        route_decision["decision"] = "HOLD_EVIDENCE"
        route_decision["reason"] = "Local receipt memory reported failure signals; route is held pending review."
        route_decision["can_recommend_as_candidate"] = False
    if overlay.decision_effect == "DOWNGRADE_TO_BLOCK":
        route_decision["decision"] = "BLOCK_HIGH_RISK_DOMAIN"
        route_decision["reason"] = "Local receipt memory reported blocked outcome or high-risk failure signal."
        route_decision["can_rank"] = False
        route_decision["can_compare"] = False
        route_decision["can_recommend_as_candidate"] = False
    updated["route_decision"] = route_decision
    return updated


def build_receipt_route_overlay(
    request: ObjectiveRouteRequest,
    route_response: dict[str, Any],
    store: ExecutionReceiptStore | None = None,
) -> ReceiptRouteOverlay:
    store = store or ExecutionReceiptStore()
    overlays: list[ReceiptCapabilityOverlay] = []
    for card in route_response.get("results", []):
        memory = store.summarize_by_capability(_capability_id_for_card(card))
        overlays.append(_effect_from_memory(card, memory))
    return ReceiptRouteOverlay(
        route_request=request.model_dump(mode="json"),
        original_route_summary=route_response.get("route_summary", {}),
        receipt_memory_applied=any(item.receipt_count > 0 for item in overlays),
        per_capability_overlay=overlays,
    )


def route_objective_with_receipts(
    request: ObjectiveRouteRequest,
    store: ExecutionReceiptStore | None = None,
) -> dict[str, Any]:
    response = route_objective(request).model_dump(mode="json", by_alias=True)
    overlay = build_receipt_route_overlay(request, response, store=store)
    updated_results = []
    overlay_by_id = {item.capability_id: item for item in overlay.per_capability_overlay}
    for card in response.get("results", []):
        updated_results.append(_apply_overlay_to_card(card, overlay_by_id.get(_capability_id_for_card(card), ReceiptCapabilityOverlay(capability_id=_capability_id_for_card(card)))))
    response["results"] = updated_results
    response["receipt_route_overlay"] = overlay.model_dump(mode="json", by_alias=True)
    response["known_limits"] = list(response.get("known_limits", [])) + [
        "Execution receipts are local memory, not independent verification.",
        "Receipts can add warnings or downgrade routes; they cannot certify or authorize actions.",
    ]
    return response
