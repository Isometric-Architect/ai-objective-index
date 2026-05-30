from ai_objective_index import aoi_030a2_marker_sync as sync


def test_marker_sync_passes_current_metadata():
    result = sync.run_marker_sync(write_result=False)

    assert result["decision"] == "PASS_MARKER_SYNCED_030A2"
    assert result["after"]["readme_mcp_name"] == sync.CANONICAL_MCP_NAME
    assert result["after"]["server_package_version"] == sync.TARGET_VERSION


def test_marker_sync_reports_version_mismatch(monkeypatch):
    monkeypatch.setattr(
        sync,
        "current_marker_state",
        lambda: {
            "pyproject_version": "0.3.0a1",
            "init_version": "0.3.0a2",
            "server_name": sync.CANONICAL_MCP_NAME,
            "server_version": "0.3.0a2",
            "server_package_registry_type": "pypi",
            "server_package_identifier": sync.PACKAGE_NAME,
            "server_package_version": "0.3.0a2",
            "readme_mcp_name": sync.CANONICAL_MCP_NAME,
        },
    )

    result = sync.run_marker_sync(write_result=False)

    assert result["decision"] == "HOLD_MARKER_SYNC_REQUIRED"
    assert "pyproject_version" in result["missing_or_mismatched"]
