from pathlib import Path

from ai_objective_index.portfolio.external_share_refresh_builder import generate_external_share_refresh


def test_external_share_refresh_builder_creates_v2_artifacts():
    result = generate_external_share_refresh(write_result=True)
    assert result["manifest"]["artifact_count"] >= 19
    assert Path("external_share_pack_v2/README_EXTERNAL_SAFE_DEMO_V2.md").exists()
    assert Path("external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.html").exists()
    assert Path("external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.md").exists()
    assert Path("external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_DASHBOARD_V2.json").exists()


def test_external_share_refresh_html_is_static_and_shows_statuses():
    generate_external_share_refresh(write_result=True)
    html = Path("external_share_pack_v2/RESIDUALOPS_EXTERNAL_SAFE_DEMO_V2.html").read_text(encoding="utf-8")
    lowered = html.lower()
    assert "claim ceiling" in lowered
    assert "agentsec" in lowered
    assert "executed" in lowered
    assert "incorporated" in lowered
    assert "qira" in lowered
    assert "datacapsule" in lowered
    assert "portfolio" in lowered
    assert "skipped_missing_artifact" in lowered
    assert "<script" not in lowered
    assert "<link" not in lowered
    assert "<form" not in lowered
    assert "https://" not in lowered
