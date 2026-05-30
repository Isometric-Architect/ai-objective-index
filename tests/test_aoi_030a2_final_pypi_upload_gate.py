from ai_objective_index import aoi_030a2_final_pypi_upload_gate as gate


READY_PREFLIGHT = {"decision": "PASS_READY_FOR_FINAL_PYPI_UPLOAD"}
READY_BUILD = {"decision": "PASS_FINAL_BUILD_READY"}


def _patch_safe(monkeypatch):
    monkeypatch.setattr(gate, "dist_paths_exist", lambda: {"wheel_exists": True, "sdist_exists": True})
    monkeypatch.setattr(gate, "pypirc_exists", lambda: False)
    monkeypatch.setattr(gate, "token_file_candidates", lambda: [])


def test_final_upload_gate_requires_env(monkeypatch):
    _patch_safe(monkeypatch)

    result = gate.run_final_pypi_upload_gate(
        env={},
        pypi_checker=lambda: {"checked": True, "status": "PASS_VERSION_AVAILABLE", "versions": []},
        token_scanner=lambda: [],
        preflight_result=READY_PREFLIGHT,
        build_result=READY_BUILD,
        write_result=False,
    )

    assert result["decision"] == "HOLD_ENV_CONFIRM_REQUIRED"
    assert result["upload_performed"] is False


def test_final_upload_gate_existing_version_holds(monkeypatch):
    _patch_safe(monkeypatch)

    result = gate.run_final_pypi_upload_gate(
        env={gate.CONFIRM_PYPI_ENV: "YES"},
        pypi_checker=lambda: {"checked": True, "status": "HOLD_VERSION_ALREADY_EXISTS", "versions": ["0.3.0a2"]},
        token_scanner=lambda: [],
        preflight_result=READY_PREFLIGHT,
        build_result=READY_BUILD,
        write_result=False,
    )

    assert result["decision"] == "HOLD_VERSION_ALREADY_EXISTS"


def test_final_upload_gate_blocks_token_findings(monkeypatch):
    _patch_safe(monkeypatch)

    result = gate.run_final_pypi_upload_gate(
        env={gate.CONFIRM_PYPI_ENV: "YES"},
        pypi_checker=lambda: {"checked": True, "status": "PASS_VERSION_AVAILABLE", "versions": []},
        token_scanner=lambda: ["secrets.txt"],
        preflight_result=READY_PREFLIGHT,
        build_result=READY_BUILD,
        write_result=False,
    )

    assert result["decision"] == "BLOCK_SECRET_FINDING"

