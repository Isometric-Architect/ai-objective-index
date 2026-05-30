from pathlib import Path

from ai_objective_index.portfolio.external_share_refresh_builder import generate_external_share_refresh
from ai_objective_index.portfolio.external_share_refresh_manifest import build_refresh_manifest


def test_external_share_refresh_manifest_records_paths_and_checksums():
    generate_external_share_refresh(write_result=True)
    manifest = build_refresh_manifest([Path("external_share_pack_v2") / "README_EXTERNAL_SAFE_DEMO_V2.md"], write_result=False)
    assert manifest["artifact_count"] == 1
    assert manifest["artifacts"][0]["sha256"]
    assert manifest["artifacts"][0]["safe_to_share_publicly"] is True
