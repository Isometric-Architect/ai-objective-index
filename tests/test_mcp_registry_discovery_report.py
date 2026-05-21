from ai_objective_index import mcp_registry_discovery_report as report


def test_discovery_report_includes_claim_boundary(monkeypatch):
    monkeypatch.setattr(report, "_read_json", lambda path: {"decision": "PASS_REGISTRY_ENTRY_VERIFIED", "mcp_registry_submission_performed": True})

    result = report.run_mcp_registry_discovery_report(write_result=False)

    assert "not verified" in result["claim_boundary"]
    assert "not security certified" in result["claim_boundary"]
    assert "quality guarantee" in " ".join(result["claim_boundary"])
    assert "certified" not in result["registry_status"].lower()
