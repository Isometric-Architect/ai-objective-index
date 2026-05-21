from ai_objective_index.vnext_distribution_gate import run_vnext_distribution_gate


def test_vnext_distribution_gate_structure():
    result = run_vnext_distribution_gate(write_result=True)
    assert result["overall_token"] in {"PASS", "HOLD", "BLOCK"}
    assert result["pypi_upload_performed"] is False
    assert result["mcp_registry_submission_performed"] is False
    assert "surface_sync" in result["checks"]
