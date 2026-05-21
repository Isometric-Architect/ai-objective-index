from pathlib import Path


def test_package_8r_b_docs_exist():
    assert Path("docs/package_8r_b_mcp_registry_submit.md").exists()
    assert Path("docs/mcp_publisher_windows_setup.md").exists()
    assert Path("docs/mcp_registry_submit_runbook.md").exists()
    assert Path("docs/mcp_registry_failure_recovery.md").exists()


def test_package_8r_b_wave13_outputs_exist_after_generation():
    root = Path("public_launch/wave13_mcp_registry_submit")
    expected = [
        "MCP_PUBLISHER_INSTALL_RESULT.json",
        "MCP_REGISTRY_PUBLISH_PREFLIGHT.json",
        "MCP_REGISTRY_SUBMIT_RESULT.json",
        "MCP_REGISTRY_SUBMIT_RECONCILE_RESULT.json",
        "MCP_REGISTRY_DISCOVERY_REPORT.json",
        "PACKAGE_8R_B_MCP_REGISTRY_SUBMIT_SUMMARY.md",
        "MCP_REGISTRY_FAILURE_RECOVERY_PLAN.md",
    ]
    for name in expected:
        assert (root / name).exists()
