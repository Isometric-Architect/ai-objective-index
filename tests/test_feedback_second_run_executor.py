from ai_objective_index.portfolio.feedback_second_run_executor import run_feedback_second_run_bridge


def test_executor_generates_selected_result_and_skipped_reports():
    result = run_feedback_second_run_bridge(sample=True, write_result=True)
    summary = result["receipt"]["aggregate_summary"]
    assert summary["selected_count"] == 1
    assert summary["skipped_count"] == 3
    assert summary["executed_count"] == 1
    assert summary["external_action_count"] == 0
    assert result["selected_results"][0]["vertical"] == "agentsec"
    assert {item["vertical"] for item in result["skipped_reports"]} == {"qira", "datacapsule", "portfolio"}
