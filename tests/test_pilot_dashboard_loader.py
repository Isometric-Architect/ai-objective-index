from ai_objective_index.portfolio.pilot_dashboard_loader import load_dashboard_sources


def test_dashboard_loader_loads_current_artifacts():
    loaded = load_dashboard_sources()
    assert len(loaded["verticals"]) == 3
    assert loaded["gates"]["second_run_gate"] == "PASS_LOCAL_SECOND_RUN_RECEIPT_READY"


def test_dashboard_loader_missing_artifact_can_hold(monkeypatch):
    import ai_objective_index.portfolio.pilot_dashboard_loader as loader

    monkeypatch.setattr(loader, "VERTICAL_RECEIPT_PATHS", {"missing": loader.Path("missing.json")})
    loaded = loader.load_dashboard_sources()
    assert "missing.json" in loaded["missing_artifacts"]
