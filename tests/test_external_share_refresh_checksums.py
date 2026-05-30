from pathlib import Path

from ai_objective_index.portfolio.external_share_refresh_builder import generate_external_share_refresh
from ai_objective_index.portfolio.external_share_refresh_checksums import build_refresh_checksums


def test_external_share_refresh_checksums_generated():
    generate_external_share_refresh(write_result=True)
    checksums = build_refresh_checksums([Path("external_share_pack_v2") / "README_EXTERNAL_SAFE_DEMO_V2.md"], write_result=False)
    assert checksums["checksum_count"] == 1
    assert "external_share_pack_v2/README_EXTERNAL_SAFE_DEMO_V2.md" in checksums["checksums"]
