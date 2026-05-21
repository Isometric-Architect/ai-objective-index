from ai_objective_index.vnext.execution_receipt_loop import (
    CapabilityReceiptMemory,
    ExecutionReceiptValidationResult,
    ReceiptRouteOverlay,
)


def test_receipt_loop_models_expose_claim_boundaries():
    validation = ExecutionReceiptValidationResult(
        receipt_id="receipt:test",
        valid=True,
        decision="RECEIPT_ACCEPTED",
    )
    assert validation.can_upgrade_to_verified is False
    assert validation.can_certify_security is False

    memory = CapabilityReceiptMemory(capability_id="capability:test")
    assert "verified" in memory.must_not_claim

    overlay = ReceiptRouteOverlay(route_request={}, original_route_summary={})
    assert overlay.external_execution is False
    assert overlay.probe_execution is False
