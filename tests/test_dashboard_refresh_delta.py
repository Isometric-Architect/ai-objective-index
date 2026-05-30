from ai_objective_index.portfolio.dashboard_refresh_delta import build_dashboard_refresh_delta, delta_to_jsonable
from ai_objective_index.portfolio.dashboard_refresh_loader import load_dashboard_refresh_sources


def test_dashboard_refresh_delta_serializes_feedback_bridge_counts():
    delta = delta_to_jsonable(build_dashboard_refresh_delta(load_dashboard_refresh_sources()))
    assert delta["schema"] == "ResidualOps_DashboardRefreshDelta/v0.1"
    assert delta["aggregate_after"]["feedback_bridge_selected_count"] == 1
    assert delta["aggregate_after"]["feedback_bridge_skipped_count"] == 3
    assert delta["no_external_action"] is True
