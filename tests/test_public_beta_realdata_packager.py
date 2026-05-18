from pathlib import Path

from ai_objective_index.public_beta_realdata_packager import create_public_beta_realdata_pack


def test_public_beta_realdata_packager_creates_v0_2_pack():
    result = create_public_beta_realdata_pack()
    release_dir = Path(result["release_dir"])

    assert release_dir.exists()
    assert (release_dir / "README_PUBLIC_BETA_v0_2.md").exists()
    assert (release_dir / "CHECKSUMS_v0_2.json").exists()
    assert result["actual_publish_performed"] is False
    readme = (release_dir / "README_PUBLIC_BETA_v0_2.md").read_text(encoding="utf-8").lower()
    assert "not verified" in readme
    assert "not security certified" in readme
    assert "not quality guaranteed" in readme
