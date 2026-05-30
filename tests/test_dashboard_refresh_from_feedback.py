from ai_objective_index.portfolio.dashboard_refresh_from_feedback import refresh_dashboard_from_feedback


def test_dashboard_refresh_from_feedback_generates_artifacts():
    result = refresh_dashboard_from_feedback(write_result=True)
    assert result["delta"]["aggregate_after"]["feedback_bridge_executed_count"] == 1
    assert result["status_cards"]["card_count"] == 4
    assert result["memory_summary"]["skipped_missing_artifact_count"] == 3
    assert result["redaction"]["decision"] == "PASS_REDACTED"
    assert result["claim_audit"]["decision"] == "PASS_CLAIM_BOUNDARY_CLEAN"
