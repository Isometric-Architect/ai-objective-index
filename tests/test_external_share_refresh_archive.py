from pathlib import Path

from ai_objective_index.portfolio import external_share_refresh_archive as archive_module
from ai_objective_index.portfolio.external_share_refresh_archive import run_refresh_archive
from ai_objective_index.portfolio.external_share_refresh_builder import generate_external_share_refresh


def test_external_share_refresh_archive_dry_run_does_not_build():
    generate_external_share_refresh(write_result=True)
    result = run_refresh_archive(dry_run=True, build=False, write_result=True)
    assert result["result_token"] == "DRY_RUN_ONLY"
    assert result["archive_built"] is False


def test_external_share_refresh_archive_build_uses_safe_files_in_mock(monkeypatch):
    written = []

    class FakeZip:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def write(self, source, arcname):
            written.append((str(source), arcname))

    monkeypatch.setattr(archive_module, "_safe_artifact_paths", lambda: [Path("external_share_pack_v2") / "README_EXTERNAL_SAFE_DEMO_V2.md"])
    monkeypatch.setattr(archive_module, "scan_refresh_share_artifacts", lambda paths, write_result=False: {"decision": "PASS_REDACTED"})
    monkeypatch.setattr(archive_module.zipfile, "ZipFile", FakeZip)
    monkeypatch.setattr(archive_module, "sha256_file", lambda path: "fake-sha256")
    result = run_refresh_archive(dry_run=False, build=True, write_result=True)
    assert result["archive_built"] is True
    assert result["included_file_count"] == 1
    assert written[0][1] == "README_EXTERNAL_SAFE_DEMO_V2.md"
