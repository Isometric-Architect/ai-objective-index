from pathlib import Path

from ai_objective_index.vnext_claim_audit import run_vnext_claim_audit


def test_package_9a_vnext_assets_and_claim_audit():
    result = run_vnext_claim_audit()

    assert result["overall_token"] == "PASS"
    assert result["pypi_upload_performed"] is False
    assert result["mcp_registry_submission_performed"] is False
    assert Path("docs/vnext/aoi_vnext_strategy.md").exists()
    assert Path("schemas/vnext/objective_card.schema.json").exists()
    assert Path("public_launch/wave3/VNEXT_PACKAGE_HOLD_NOTE.md").exists()
    text = Path("public_launch/wave3/VNEXT_PACKAGE_HOLD_NOTE.md").read_text(encoding="utf-8")
    assert "PyPI upload and MCP Registry submission are paused" in text
