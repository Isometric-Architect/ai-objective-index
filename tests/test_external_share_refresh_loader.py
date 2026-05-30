from pathlib import Path

from ai_objective_index.portfolio.external_share_refresh_loader import load_external_share_refresh_sources


def test_external_share_refresh_loader_loads_roe21_artifacts():
    loaded = load_external_share_refresh_sources()
    assert loaded["decision"] == "PASS_REFRESHED_DASHBOARD_LOADED"
    assert loaded["dashboard_refresh_delta"]["schema"] == "ResidualOps_DashboardRefreshDelta/v0.1"
    assert loaded["status_cards"]["card_count"] == 4


def test_external_share_refresh_loader_holds_when_refresh_missing():
    loaded = load_external_share_refresh_sources(paths=[Path("pilot_dashboard") / "ROE21_MISSING.json"])
    assert loaded["decision"] == "HOLD_MISSING_REFRESHED_DASHBOARD"
    assert loaded["missing_roe21_artifacts"]
