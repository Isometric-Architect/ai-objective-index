from ai_objective_index.vnext.execution_receipt_loop import ExecutionReceiptSubmission
from ai_objective_index.vnext.execution_receipt_store import ExecutionReceiptStore
from ai_objective_index.vnext.execution_receipt_validation import validate_execution_receipt


def test_capability_memory_summarizes_failure(tmp_path):
    store = ExecutionReceiptStore(tmp_path / "receipts.jsonl", tmp_path / "index.json")
    receipt = ExecutionReceiptSubmission(
        capability_id="capability:test",
        outcome="fail",
        receipt_origin="public_issue",
        error_type="install_failure",
        outcome_summary="Install failed in a local environment.",
    )
    store.append_receipt(receipt, validate_execution_receipt(receipt))
    memory = store.summarize_by_capability("capability:test")
    assert memory["memory_status"] == "FAILURE_SIGNALS"
    assert memory["outcome_counts"]["fail"] == 1
    assert "install_failure" in memory["recurring_error_types"]
