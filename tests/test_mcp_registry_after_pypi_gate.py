from ai_objective_index import mcp_registry_after_pypi_gate


def _server(version="0.3.0a1"):
    return {
        "name": "io.github.isometric-architect/ai-objective-index",
        "version": version,
        "packages": [{"registryType": "pypi", "identifier": "ai-objective-index", "version": version}],
    }


def test_mcp_registry_after_pypi_gate_success_or_publisher_hold(monkeypatch):
    def fake_read_json(path):
        name = str(path)
        if "UPLOAD" in name:
            return {"result_token": "UPLOAD_SUCCESS"}
        if "INSTALL" in name:
            return {"decision": "PASS_REAL_PYPI_INSTALL"}
        if "server.json" in name:
            return _server()
        return {}

    monkeypatch.setattr(mcp_registry_after_pypi_gate, "_read_json", fake_read_json)
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "_read", lambda path: "<!-- mcp-name: io.github.isometric-architect/ai-objective-index -->")
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "_claim_guard_passed", lambda: True)
    monkeypatch.setattr(mcp_registry_after_pypi_gate.shutil, "which", lambda name: None)

    result = mcp_registry_after_pypi_gate.run_mcp_registry_after_pypi_gate(write_result=False)

    assert result["decision"] == "HOLD_MCP_PUBLISHER_REQUIRED"
    assert result["mcp_registry_submission_performed"] is False


def test_mcp_registry_after_pypi_gate_missing_install_holds(monkeypatch):
    def fake_read_json(path):
        name = str(path)
        if "UPLOAD" in name:
            return {"result_token": "UPLOAD_SUCCESS"}
        if "INSTALL" in name:
            return {"decision": "BLOCK_INSTALL_FAILED"}
        if "server.json" in name:
            return _server()
        return {}

    monkeypatch.setattr(mcp_registry_after_pypi_gate, "_read_json", fake_read_json)
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "_read", lambda path: "<!-- mcp-name: io.github.isometric-architect/ai-objective-index -->")
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "_claim_guard_passed", lambda: True)

    result = mcp_registry_after_pypi_gate.run_mcp_registry_after_pypi_gate(write_result=False)

    assert result["decision"] == "HOLD_REAL_PYPI_INSTALL_VERIFY_FIRST"


def test_mcp_registry_after_pypi_gate_metadata_mismatch_blocks(monkeypatch):
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "_read_json", lambda path: {"result_token": "UPLOAD_SUCCESS", "decision": "PASS_REAL_PYPI_INSTALL"})
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "_read_server_json", lambda: _server("0.2.0"))
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "_read", lambda path: "<!-- mcp-name: io.github.isometric-architect/ai-objective-index -->")
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "tracked_token_findings", lambda: [])
    monkeypatch.setattr(mcp_registry_after_pypi_gate, "_claim_guard_passed", lambda: True)

    result = mcp_registry_after_pypi_gate.run_mcp_registry_after_pypi_gate(write_result=False)

    assert result["decision"] == "BLOCK_METADATA_MISMATCH"
