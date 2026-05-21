from ai_objective_index import mcp_registry_publish_preflight as preflight


def _result(decision):
    return {"decision": decision}


def test_preflight_all_dependencies_pass(monkeypatch):
    def fake_read_json(path):
        name = str(path)
        if "INSTALL" in name:
            return _result("PASS_MCP_PUBLISHER_AVAILABLE")
        if "AUTH" in name:
            return _result("PASS_AUTH_CONFIRMED")
        if "MANIFEST" in name:
            return _result("PASS_MANIFEST_READY")
        if "PROTECTION" in name:
            return _result("PASS_READY_FOR_MCP_REGISTRY_AFTER_PROTECTION")
        if "PYPI" in name:
            return _result("PASS_REAL_PYPI_RELEASE_VERIFIED")
        return {}

    monkeypatch.setattr(preflight, "_read_json", fake_read_json)
    monkeypatch.setattr(preflight, "find_mcp_publisher", lambda: "mcp-publisher")
    monkeypatch.setattr(preflight, "_no_secret_real_findings", lambda: True)
    monkeypatch.setattr(preflight, "_claim_guard_passed", lambda: True)

    result = preflight.run_mcp_registry_publish_preflight(write_result=False)

    assert result["decision"] == "PASS_READY_TO_SUBMIT"


def test_preflight_protection_missing_holds(monkeypatch):
    monkeypatch.setattr(preflight, "_read_json", lambda path: _result("HOLD_PRIVATE_SPLIT_REVIEW") if "PROTECTION" in str(path) else _result("PASS_REAL_PYPI_RELEASE_VERIFIED"))
    monkeypatch.setattr(preflight, "find_mcp_publisher", lambda: "mcp-publisher")
    monkeypatch.setattr(preflight, "_no_secret_real_findings", lambda: True)
    monkeypatch.setattr(preflight, "_claim_guard_passed", lambda: True)

    result = preflight.run_mcp_registry_publish_preflight(write_result=False)

    assert result["decision"] in {"HOLD_PROTECTION_GATE_NOT_PASS", "BLOCK_MANIFEST_MISMATCH"}


def test_preflight_manifest_mismatch_blocks(monkeypatch):
    def fake_read_json(path):
        if "MANIFEST" in str(path):
            return _result("BLOCK_METADATA_MISMATCH")
        if "PROTECTION" in str(path):
            return _result("PASS_READY_FOR_MCP_REGISTRY_AFTER_PROTECTION")
        if "PYPI" in str(path):
            return _result("PASS_REAL_PYPI_RELEASE_VERIFIED")
        if "INSTALL" in str(path):
            return _result("PASS_MCP_PUBLISHER_AVAILABLE")
        if "AUTH" in str(path):
            return _result("PASS_AUTH_CONFIRMED")
        return {}

    monkeypatch.setattr(preflight, "_read_json", fake_read_json)
    monkeypatch.setattr(preflight, "find_mcp_publisher", lambda: "mcp-publisher")
    monkeypatch.setattr(preflight, "_no_secret_real_findings", lambda: True)
    monkeypatch.setattr(preflight, "_claim_guard_passed", lambda: True)

    result = preflight.run_mcp_registry_publish_preflight(write_result=False)

    assert result["decision"] == "BLOCK_MANIFEST_MISMATCH"


def test_preflight_secret_finding_blocks(monkeypatch):
    monkeypatch.setattr(preflight, "_read_json", lambda path: _result("PASS_MANIFEST_READY"))
    monkeypatch.setattr(preflight, "_no_secret_real_findings", lambda: False)
    monkeypatch.setattr(preflight, "_claim_guard_passed", lambda: True)

    result = preflight.run_mcp_registry_publish_preflight(write_result=False)

    assert result["decision"] == "BLOCK_SECRET_FINDING"
