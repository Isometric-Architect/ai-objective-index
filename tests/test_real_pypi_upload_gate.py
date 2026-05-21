from pathlib import Path

from ai_objective_index import real_pypi_upload_gate


def _prepare_dist(tmp_path: Path) -> Path:
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "ai_objective_index-0.3.0a1-py3-none-any.whl").write_text("wheel", encoding="utf-8")
    (dist / "ai_objective_index-0.3.0a1.tar.gz").write_text("sdist", encoding="utf-8")
    return tmp_path


def _patch_metadata(monkeypatch, tmp_path: Path, version: str = "0.3.0a1") -> None:
    monkeypatch.setattr(real_pypi_upload_gate, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        real_pypi_upload_gate,
        "_read_pyproject",
        lambda: {"project": {"name": "ai-objective-index", "version": version}},
    )
    monkeypatch.setattr(
        real_pypi_upload_gate,
        "_read_server_json",
        lambda: {
            "version": version,
            "packages": [{"registryType": "pypi", "identifier": "ai-objective-index", "version": version}],
        },
    )
    monkeypatch.setattr(real_pypi_upload_gate, "_import_version", lambda: version)


def test_real_pypi_upload_gate_passes_when_project_available(monkeypatch, tmp_path):
    _prepare_dist(tmp_path)
    _patch_metadata(monkeypatch, tmp_path)
    result = real_pypi_upload_gate.evaluate_real_pypi_upload_gate(
        pypi_status_checker=lambda: {"status": "PROJECT_AVAILABLE_OR_NEW", "checked": True},
        twine_checker=lambda: {"ok": True},
        token_scanner=lambda: [],
        write_result=False,
    )

    assert result["decision"] == "PASS_READY_FOR_REAL_PYPI_UPLOAD"
    assert result["upload_performed"] is False


def test_real_pypi_upload_gate_version_mismatch_blocks(monkeypatch, tmp_path):
    _prepare_dist(tmp_path)
    _patch_metadata(monkeypatch, tmp_path, version="0.2.0")
    result = real_pypi_upload_gate.evaluate_real_pypi_upload_gate(
        pypi_status_checker=lambda: {"status": "PROJECT_AVAILABLE_OR_NEW", "checked": True},
        twine_checker=lambda: {"ok": True},
        token_scanner=lambda: [],
        write_result=False,
    )

    assert result["decision"] == "BLOCK_VERSION_MISMATCH"


def test_real_pypi_upload_gate_token_like_file_blocks(monkeypatch, tmp_path):
    _prepare_dist(tmp_path)
    _patch_metadata(monkeypatch, tmp_path)
    result = real_pypi_upload_gate.evaluate_real_pypi_upload_gate(
        pypi_status_checker=lambda: {"status": "PROJECT_AVAILABLE_OR_NEW", "checked": True},
        twine_checker=lambda: {"ok": True},
        token_scanner=lambda: ["leaked_token.txt"],
        write_result=False,
    )

    assert result["decision"] == "BLOCK_TOKEN_FILE_FOUND"


def test_real_pypi_upload_gate_project_name_taken_blocks(monkeypatch, tmp_path):
    _prepare_dist(tmp_path)
    _patch_metadata(monkeypatch, tmp_path)
    result = real_pypi_upload_gate.evaluate_real_pypi_upload_gate(
        pypi_status_checker=lambda: {"status": "BLOCK_PROJECT_NAME_TAKEN", "checked": True},
        twine_checker=lambda: {"ok": True},
        token_scanner=lambda: [],
        write_result=False,
    )

    assert result["decision"] == "BLOCK_PROJECT_NAME_TAKEN"


def test_real_pypi_upload_gate_existing_same_version_holds(monkeypatch, tmp_path):
    _prepare_dist(tmp_path)
    _patch_metadata(monkeypatch, tmp_path)
    result = real_pypi_upload_gate.evaluate_real_pypi_upload_gate(
        pypi_status_checker=lambda: {"status": "HOLD_VERSION_ALREADY_EXISTS", "checked": True},
        twine_checker=lambda: {"ok": True},
        token_scanner=lambda: [],
        write_result=False,
    )

    assert result["decision"] == "HOLD_VERSION_ALREADY_EXISTS"
