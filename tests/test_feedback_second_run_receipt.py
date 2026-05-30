from ai_objective_index.portfolio.feedback_second_run_receipt import FeedbackSecondRunReceipt, receipt_to_jsonable


def test_feedback_second_run_receipt_serializes():
    receipt = FeedbackSecondRunReceipt(
        bridge_id="bridge-test",
        selected_results=[{"vertical": "agentsec"}],
        skipped_reports=[{"vertical": "qira"}],
        aggregate_summary={"selected_count": 1, "skipped_count": 1, "executed_count": 1, "external_action_count": 0},
    )
    payload = receipt_to_jsonable(receipt)
    assert payload["schema"] == "ResidualOps_FeedbackSecondRunReceipt/v0.1"
    assert payload["mode"] == "local_feedback_second_run"
    assert payload["claim_boundary"]["not_external_pilot"] is True
