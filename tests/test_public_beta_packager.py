import json
from pathlib import Path

from ai_objective_index.public_beta_packager import create_public_beta_pack


def test_public_beta_packager_creates_release_files():
    result = create_public_beta_pack()
    release_dir = Path(result["release_dir"])

    assert release_dir.exists()
    assert (release_dir / "FILE_MANIFEST.json").exists()
    assert (release_dir / "CHECKSUMS.json").exists()
    assert (release_dir / "README_PUBLIC_BETA.md").exists()
    readme = (release_dir / "README_PUBLIC_BETA.md").read_text(encoding="utf-8").lower()
    assert "read-only" in readme
    assert "not a quality guarantee" in readme

    manifest = json.loads((release_dir / "FILE_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["file_count"] >= 8
    assert result["actual_publish_performed"] is False
