from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_agentsec4_docs_exist():
    for relative in [
        "docs/agentsec4_policy_profile_pack.md",
        "docs/agentsec_mcp_manifest_hardening.md",
    ]:
        assert (ROOT / relative).exists()


def test_agentsec4_outputs_exist_after_generation():
    for relative in [
        "public_launch/agentsec4/AGENTSEC4_PROFILE_PACK.json",
        "public_launch/agentsec4/AGENTSEC4_PROFILE_PACK.md",
        "public_launch/agentsec4/AGENTSEC4_MCP_MANIFEST_HARDENING_RESULT.json",
        "public_launch/agentsec4/AGENTSEC4_MCP_MANIFEST_HARDENING_REPORT.md",
        "public_launch/agentsec4/AGENTSEC4_PACKAGE_RESULT.json",
        "public_launch/agentsec4/AGENTSEC4_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists()


def test_agentsec4_docs_preserve_claim_boundary():
    text = (ROOT / "docs" / "agentsec_mcp_manifest_hardening.md").read_text(encoding="utf-8")

    assert "not a live security scanner" in text
    assert "action authorization" in text
