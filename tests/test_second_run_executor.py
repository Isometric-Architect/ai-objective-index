from ai_objective_index.portfolio.second_run_executor import run_second_run


def test_second_run_executor_generates_all_three_vertical_outputs():
    result = run_second_run(sample=True, write_result=True)
    verticals = {item["vertical"] for item in result["vertical_results"]}
    assert verticals == {"agentsec", "qira", "datacapsule"}
    assert all(item["external_actions_performed"] is False for item in result["vertical_results"])
    assert result["redaction"]["decision"] == "PASS_REDACTED"
