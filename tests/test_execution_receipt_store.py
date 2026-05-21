from pathlib import Path

from ai_objective_index.vnext.execution_receipt_loop import ExecutionReceiptSubmission
from ai_objective_index.vnext.execution_receipt_store import ExecutionReceiptStore
from ai_objective_index.vnext.execution_receipt_validation import validate_execution_receipt


def _store(tmp_path: Path) -> ExecutionReceiptStore:
    return ExecutionReceiptStore(tmp_path / "receipts.jsonl", tmp_path / "index.json")


def test_receipt_store_appends_and_lists(tmp_path):
    store = _store(tmp_path)
    receipt = ExecutionReceiptSubmission(
        objective_id="objective:test",
        capability_id="capability:test",
        outcome="fail",
        receipt_origin="public_issue",
        error_type="policy_unclear",
        outcome_summary="Policy field missing.",
    )
    validation = validate_execution_receipt(receipt)
    store.append_receipt(receipt, validation)

    listed = store.list_receipts(capability_id="capability:test")
    assert len(listed) == 1
    assert listed[0]["receipt"]["capability_id"] == "capability:test"
    assert store.get_receipt(receipt.receipt_id)["validation"]["can_upgrade_to_verified"] is False


def test_receipt_store_redacts_token_like_strings(tmp_path):
    store = _store(tmp_path)
    receipt = ExecutionReceiptSubmission(
        capability_id="capability:test",
        outcome="hold",
        observed_outputs=["token: ghp_123456789012345678901234567890123456"],
    )
    validation = validate_execution_receipt(receipt)
    record = store.append_receipt(receipt, validation)
    text = str(record.model_dump(mode="json", by_alias=True))
    assert "ghp_1234567890" not in text
    assert "REDACTED_TOKEN_LIKE_TEXT" in text


def test_receipt_store_objective_summary(tmp_path):
    store = _store(tmp_path)
    receipt = ExecutionReceiptSubmission(objective_id="objective:test", capability_id="capability:test", outcome="hold")
    store.append_receipt(receipt, validate_execution_receipt(receipt))
    summary = store.summarize_by_objective("objective:test")
    assert summary["receipt_count"] == 1
    assert "capability:test" in summary["capabilities_seen"]
