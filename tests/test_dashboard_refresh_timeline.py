from ai_objective_index.portfolio.dashboard_refresh_loader import load_dashboard_refresh_sources
from ai_objective_index.portfolio.dashboard_refresh_timeline import build_dashboard_refresh_timeline


def test_dashboard_refresh_timeline_includes_bridge_and_refresh_events():
    timeline = build_dashboard_refresh_timeline(load_dashboard_refresh_sources())
    phases = [event["phase"] for event in timeline["events"]]
    assert "feedback_second_run_bridge" in phases
    assert "dashboard_refresh" in phases
    bridge = next(event for event in timeline["events"] if event["phase"] == "feedback_second_run_bridge")
    assert bridge["selected_count"] == 1
    assert bridge["skipped_count"] == 3
