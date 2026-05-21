from ai_objective_index import mcp_registry_readiness_refresh


def test_mcp_registry_readiness_holds_before_pypi(monkeypatch):
    def fake_read_json(path):
        name = str(path)
        if name.endswith("server.json"):
            return {
                "name": "io.github.Isometric-Architect/ai-objective-index",
                "version": "0.3.0a1",
                "packages": [{"registryType": "pypi", "identifier": "ai-objective-index", "version": "0.3.0a1"}],
            }
        if "PYPI_READINESS" in name:
            return {"decision": "HOLD_TESTPYPI_ACCOUNT_REQUIRED"}
        if "DIST_BUILD" in name:
            return {"decision": "PASS_BUILD_READY"}
        return {}

    monkeypatch.setattr(mcp_registry_readiness_refresh, "_read_json", fake_read_json)
    monkeypatch.setattr(mcp_registry_readiness_refresh, "_read", lambda path: "<!-- mcp-name: io.github.Isometric-Architect/ai-objective-index -->")
    result = mcp_registry_readiness_refresh.run_mcp_registry_readiness_refresh(write_result=False)

    assert result["decision"] == "HOLD_TESTPYPI_FIRST"
    assert result["mcp_registry_submission_performed"] is False


def test_mcp_registry_readiness_blocks_version_mismatch(monkeypatch):
    monkeypatch.setattr(
        mcp_registry_readiness_refresh,
        "_read_json",
        lambda path: {
            "name": "io.github.Isometric-Architect/ai-objective-index",
            "version": "0.2.0",
            "packages": [{"registryType": "pypi", "identifier": "ai-objective-index", "version": "0.2.0"}],
        }
        if str(path).endswith("server.json")
        else {},
    )
    monkeypatch.setattr(mcp_registry_readiness_refresh, "_read", lambda path: "<!-- mcp-name: io.github.Isometric-Architect/ai-objective-index -->")
    result = mcp_registry_readiness_refresh.run_mcp_registry_readiness_refresh(write_result=False)

    assert result["decision"] == "BLOCK_VERSION_MISMATCH"
    assert result["token_printed"] is False
