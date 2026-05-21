from ai_objective_index.vnext_surface_sync_audit import audit_surface_text, run_vnext_surface_sync_audit


def test_surface_sync_detects_missing_readme_marker():
    result = audit_surface_text("AOI is a ranking tool only.")
    assert result["required_readme"]["objective_to_capability_router"] is False


def test_surface_sync_detects_overclaim_fixture():
    result = audit_surface_text(
        "AOI is an AI Agent Capability Trust Router. This is an external security gateway."
    )
    assert "external security gateway" in result["overclaim_findings"]


def test_surface_sync_current_repo_outputs_structure():
    result = run_vnext_surface_sync_audit(write_result=True)
    assert result["overall_token"] in {"PASS", "HOLD", "BLOCK"}
    assert result["pypi_upload_performed"] is False
