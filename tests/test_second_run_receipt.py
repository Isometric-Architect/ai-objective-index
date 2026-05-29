from ai_objective_index.portfolio.second_run_executor import run_second_run


def test_second_run_receipt_serializes():
    result = run_second_run(sample=True, write_result=True)
    receipt = result["receipt"]
    assert receipt["schema"] == "ResidualOps_SecondRunReceipt/v0.1"
    assert receipt["aggregate_summary"]["vertical_count"] == 3
    assert receipt["aggregate_summary"]["prior_allow_count"] == 3
    assert receipt["aggregate_summary"]["new_allow_count"] == 3
    assert receipt["claim_boundary"]["no_external_action_authorization"] is True
