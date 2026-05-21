from ai_objective_index.vnext.execution_receipt_loop import ExecutionReceiptSubmission
from ai_objective_index.vnext.execution_receipt_store import ExecutionReceiptStore
from ai_objective_index.vnext.execution_receipt_validation import validate_execution_receipt
from ai_objective_index.vnext.objective_router_models import ObjectiveRouteRequest
from ai_objective_index.vnext.receipt_router_adapter import route_objective_with_receipts


def test_route_overlay_cannot_upgrade_hold_to_allow(tmp_path):
    store = ExecutionReceiptStore(tmp_path / "receipts.jsonl", tmp_path / "index.json")
    route = route_objective_with_receipts(
        ObjectiveRouteRequest(
            query="image API",
            objective="select source-traced API candidates",
            domain="ai_apis",
            data_scope="sample",
            limit=1,
        ),
        store=store,
    )
    card = route["results"][0]
    receipt = ExecutionReceiptSubmission(
        capability_id=card["capability_id"],
        outcome="success",
        receipt_origin="self_reported",
        route_decision_before=card["route_decision"]["decision"],
        route_decision_after="ALLOW_WITH_LIMITS",
    )
    store.append_receipt(receipt, validate_execution_receipt(receipt))
    overlay_route = route_objective_with_receipts(
        ObjectiveRouteRequest(
            query="image API",
            objective="select source-traced API candidates",
            domain="ai_apis",
            data_scope="sample",
            limit=1,
        ),
        store=store,
    )
    after = overlay_route["results"][0]["route_decision"]["decision"]
    assert after.startswith("HOLD") or after.startswith("BLOCK") or after.startswith("ALLOW")
    if card["route_decision"]["decision"].startswith("HOLD"):
        assert not after.startswith("ALLOW")
    assert overlay_route["receipt_route_overlay"]["receipt_memory_applied"] is True
