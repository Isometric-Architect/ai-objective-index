from pathlib import Path


def test_package_8s_docs_exist():
    assert Path("docs/technology_protection_policy.md").exists()
    assert Path("docs/public_private_split.md").exists()
    assert Path("docs/anti_clone_strategy.md").exists()
    assert Path("docs/package_artifact_exposure_policy.md").exists()
    assert Path("docs/license_ip_positioning.md").exists()
    assert Path("docs/mcp_registry_pre_publish_protection.md").exists()


def test_package_8s_wave12_outputs_exist_after_generation():
    root = Path("public_launch/wave12_tech_protection")
    expected = [
        "TECH_PROTECTION_AUDIT_RESULT.json",
        "PUBLIC_PRIVATE_SPLIT_AUDIT.json",
        "PACKAGE_ARTIFACT_EXPOSURE_AUDIT.json",
        "ANTI_CLONE_RISK_AUDIT.json",
        "LICENSE_IP_POSITIONING_AUDIT.json",
        "MCP_REGISTRY_PRE_PUBLISH_PROTECTION_GATE.json",
        "TECHNOLOGY_PROTECTION_SUMMARY.md",
    ]
    for name in expected:
        assert (root / name).exists()
