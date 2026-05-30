from ai_objective_index.portfolio.external_share_pack_loader import load_external_share_sources


def test_share_pack_loader_loads_roe16_artifacts():
    loaded = load_external_share_sources()
    assert loaded["decision"] == "PASS_SOURCE_DASHBOARD_LOADED"
    assert loaded["dashboard"]["schema"] == "ResidualOps_PilotDashboard/v0.1"
