import tarfile
import zipfile

from ai_objective_index import package_artifact_exposure_audit as audit


def test_safe_artifact_names_pass():
    result = audit.inspect_artifact_names(["ai_objective_index/__init__.py", "ai_objective_index-0.3.0a1.dist-info/METADATA"])

    assert result["blocked"] == []


def test_sensitive_artifact_names_block():
    result = audit.inspect_artifact_names([".env", ".pypirc", "private_kernel/weights.json"])

    assert len(result["blocked"]) == 3


def test_raw_internal_source_fixture_blocks():
    result = audit.inspect_artifact_names(["SOURCE_0513_REPACK_FINAL_v1/source.txt"])

    assert result["blocked"]


def test_package_artifact_audit_safe_fixture_passes(tmp_path, monkeypatch):
    wheel = tmp_path / "safe.whl"
    sdist = tmp_path / "safe.tar.gz"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("ai_objective_index/__init__.py", "__version__='0.3.0a1'\n")
    safe_file = tmp_path / "safe.txt"
    safe_file.write_text("safe public artifact", encoding="utf-8")
    with tarfile.open(sdist, "w:gz") as archive:
        archive.add(safe_file, arcname="ai_objective_index-0.3.0a1/README.md")

    monkeypatch.setattr(audit, "WHEEL_PATH", wheel.relative_to(tmp_path))
    monkeypatch.setattr(audit, "SDIST_PATH", sdist.relative_to(tmp_path))
    monkeypatch.setattr(audit, "_repo_root", lambda: tmp_path)

    result = audit.run_package_artifact_exposure_audit(write_result=False)

    assert result["decision"] == "PASS_PACKAGE_ARTIFACT_SAFE"
