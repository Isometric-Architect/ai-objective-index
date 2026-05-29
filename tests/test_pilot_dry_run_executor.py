from ai_objective_index.portfolio.pilot_dry_run_executor import execute_all_verticals
from ai_objective_index.portfolio.pilot_dry_run_router import route_sample_intake_packets


def test_executor_generates_all_three_vertical_results():
    routes = route_sample_intake_packets(ensure_samples=True)
    results = execute_all_verticals("dry-run-test", routes)
    assert [result.vertical for result in results] == ["agentsec", "qira", "datacapsule"]
    assert all(result.redaction_status == "PASS_REDACTED" for result in results)
    assert all(result.external_action_used is False for result in results)
