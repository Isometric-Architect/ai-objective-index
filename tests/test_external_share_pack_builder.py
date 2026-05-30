from pathlib import Path

from ai_objective_index.portfolio.external_share_pack_builder import generate_external_share_pack


def test_share_pack_builder_creates_readme_html_md_json():
    result = generate_external_share_pack(write_result=True)
    assert result["manifest"]["artifact_count"] >= 10
    assert Path("external_share_pack/README_EXTERNAL_SAFE_DEMO.md").exists()
    assert Path("external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_DEMO.html").exists()
    assert Path("external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_DEMO.md").exists()
    assert Path("external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_DASHBOARD.json").exists()


def test_share_pack_html_has_claim_ceiling_and_no_external_dependencies():
    generate_external_share_pack(write_result=True)
    html = Path("external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_DEMO.html").read_text(encoding="utf-8")
    assert "External-safe static demo" in html
    assert "<script" not in html.lower()
    assert "<link" not in html.lower()
    assert "<form" not in html.lower()
    assert "https://" not in html.lower()
