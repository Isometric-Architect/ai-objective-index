from pathlib import Path

from ai_objective_index.portfolio.dashboard_refresh_loader import load_dashboard_refresh_sources


def test_dashboard_refresh_loader_reads_roe20_artifacts():
    loaded = load_dashboard_refresh_sources()
    assert loaded["decision"] == "LOADED"
    assert loaded["bridge_receipt"]["aggregate_summary"]["selected_count"] == 1
    assert loaded["source_dashboard"]["schema"] == "ResidualOps_PilotDashboard/v0.1"


def test_dashboard_refresh_loader_holds_when_roe20_missing():
    loaded = load_dashboard_refresh_sources(paths=[Path("feedback_second_runs") / "missing-roe20.json"])
    assert loaded["decision"] == "HOLD_MISSING_FEEDBACK_SECOND_RUN"
    assert loaded["missing_roe20_artifacts"]
