from ai_objective_index.portfolio.dashboard_refresh_feedback_memory import build_dashboard_refresh_feedback_memory_summary
from ai_objective_index.portfolio.dashboard_refresh_loader import load_dashboard_refresh_sources


def test_dashboard_refresh_feedback_memory_summary_counts_statuses():
    summary = build_dashboard_refresh_feedback_memory_summary(load_dashboard_refresh_sources())
    assert summary["schema"] == "ResidualOps_DashboardRefreshFeedbackSummary/v0.1"
    assert summary["entry_count"] == 4
    assert summary["incorporated_count"] == 1
    assert summary["skipped_missing_artifact_count"] == 3
    assert summary["external_action_authorized"] is False
