from ai_objective_index.vnext.execution_receipt_loop import ExecutionReceiptSubmission
from ai_objective_index.vnext.execution_receipt_validation import validate_execution_receipt


def test_receipt_submission_serializes():
    receipt = ExecutionReceiptSubmission(capability_id="capability:test", outcome="hold")
    payload = receipt.model_dump(mode="json", by_alias=True)
    assert payload["schema"] == "AOI_ExecutionReceiptSubmission/v0.1"
    assert payload["receipt_id"].startswith("exec-receipt-")


def test_missing_capability_id_invalid():
    result = validate_execution_receipt({"capability_id": "", "outcome": "success"})
    assert result.valid is False
    assert result.decision == "INVALID_RECEIPT"


def test_forbidden_action_blocks_receipt():
    result = validate_execution_receipt(
        {
            "capability_id": "capability:test",
            "outcome": "success",
            "outcome_summary": "The tool can purchase items for the user.",
        }
    )
    assert result.valid is False
    assert result.decision == "BLOCK_FORBIDDEN_ACTION"


def test_unsupported_safety_claim_blocks_receipt():
    result = validate_execution_receipt(
        {
            "capability_id": "capability:test",
            "outcome": "success",
            "outcome_summary": "This is a safe tool for all use cases.",
        }
    )
    assert result.valid is False
    assert result.decision == "BLOCK_UNSUPPORTED_CLAIM"


def test_self_reported_success_cannot_upgrade_to_verified():
    result = validate_execution_receipt(
        {
            "capability_id": "capability:test",
            "outcome": "success",
            "receipt_origin": "self_reported",
            "outcome_summary": "It worked in one local attempt.",
        }
    )
    assert result.valid is True
    assert result.decision == "HOLD_LOW_EVIDENCE_ORIGIN"
    assert result.can_upgrade_to_verified is False
    assert result.can_certify_security is False
