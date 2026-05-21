from pathlib import Path


def test_package_8r_c_modules_exist():
    for path in [
        "src/ai_objective_index/mcp_registry_publish_diagnostics.py",
        "src/ai_objective_index/mcp_registry_direct_publish_runner.py",
        "src/ai_objective_index/mcp_registry_failure_classifier.py",
    ]:
        assert Path(path).exists()


def test_package_8r_c_wave14_assets_exist_after_diagnostics():
    wave = Path("public_launch/wave14_mcp_registry_diagnostics")
    expected = [
        "MCP_PUBLISHER_VALIDATE_RESULT.json",
        "MCP_REGISTRY_FAILURE_CLASSIFICATION.json",
        "MCP_REGISTRY_DIAGNOSTIC_SUMMARY.md",
        "MCP_REGISTRY_NEXT_RECOVERY_STEPS.md",
    ]
    missing = [name for name in expected if not (wave / name).exists()]
    assert missing == []
