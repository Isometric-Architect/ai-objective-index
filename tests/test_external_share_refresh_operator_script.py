from ai_objective_index.portfolio.external_share_refresh_operator_script import build_operator_script


def test_external_share_refresh_operator_script_names_v2_statuses():
    script = build_operator_script()
    assert "RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.html" in script
    assert "executed and incorporated" in script
    assert "skipped_missing_artifact" in script
    assert "Do not say certified" in script
