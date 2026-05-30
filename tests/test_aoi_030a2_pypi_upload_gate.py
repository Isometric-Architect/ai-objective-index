from ai_objective_index import aoi_030a2_pypi_upload_gate as gate


def _patch_ready(monkeypatch, tmp_path):
    (tmp_path / "dist").mkdir()
    (tmp_path / gate.WHEEL_PATH).write_text("wheel", encoding="utf-8")
    (tmp_path / gate.SDIST_PATH).write_text("sdist", encoding="utf-8")
    monkeypatch.setattr(gate, "repo_root", lambda: tmp_path)
    monkeypatch.setattr(gate, "run_marker_sync", lambda write_result=True: {"decision": "PASS_MARKER_SYNCED_030A2"})
    monkeypatch.setattr(gate, "read_json", lambda path: {"decision": "PASS_BUILD_TWINE_MARKER_SYNCED"})


def test_upload_gate_requires_env(monkeypatch, tmp_path):
    _patch_ready(monkeypatch, tmp_path)

    result = gate.run_pypi_upload_gate(
        env={},
        pypi_checker=lambda: {"checked": True, "status": "PASS_VERSION_AVAILABLE", "versions": ["0.3.0a1"]},
        token_scanner=lambda: [],
        write_result=False,
    )

    assert result["decision"] == "HOLD_ENV_CONFIRM_REQUIRED"
    assert result["upload_performed"] is False


def test_upload_gate_existing_version_holds(monkeypatch, tmp_path):
    _patch_ready(monkeypatch, tmp_path)

    result = gate.run_pypi_upload_gate(
        env={gate.CONFIRM_ENV: "YES"},
        pypi_checker=lambda: {"checked": True, "status": "HOLD_VERSION_ALREADY_EXISTS", "versions": ["0.3.0a2"]},
        token_scanner=lambda: [],
        write_result=False,
    )

    assert result["decision"] == "HOLD_VERSION_ALREADY_EXISTS"


def test_upload_gate_token_finding_blocks(monkeypatch, tmp_path):
    _patch_ready(monkeypatch, tmp_path)

    result = gate.run_pypi_upload_gate(
        env={gate.CONFIRM_ENV: "YES"},
        pypi_checker=lambda: {"checked": True, "status": "PASS_VERSION_AVAILABLE", "versions": []},
        token_scanner=lambda: ["token.txt"],
        write_result=False,
    )

    assert result["decision"] == "BLOCK_SECRET_FINDING"


def test_upload_gate_mocked_upload_success(monkeypatch, tmp_path):
    _patch_ready(monkeypatch, tmp_path)

    result = gate.run_pypi_upload_gate(
        env={gate.CONFIRM_ENV: "YES"},
        pypi_checker=lambda: {"checked": True, "status": "PASS_VERSION_AVAILABLE", "versions": []},
        token_scanner=lambda: [],
        upload_runner=lambda command, timeout=900: {"ok": True, "returncode": 0, "stdout": "", "stderr": ""},
        write_result=False,
    )

    assert result["decision"] == "PASS_PYPI_UPLOAD_COMPLETED"
    assert result["upload_performed"] is True
