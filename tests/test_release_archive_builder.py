from pathlib import Path

from ai_objective_index.release_archive_builder import build_release_archive


def test_release_archive_builder_creates_dist_archive():
    result = build_release_archive(create_zip=False)
    archive_dir = Path(result["archive_dir"])

    assert archive_dir.exists()
    assert result["copied_file_count"] > 0
    assert Path("data/generated/launch_archive_manifest_v0_2.json").exists()
    assert (archive_dir / "release/public_beta_v0_2/README_PUBLIC_BETA_v0_2.md").exists()
    copied_paths = [item["path"] for item in result["checksums"]]
    assert not any(".pytest_cache" in path or "__pycache__" in path for path in copied_paths)
