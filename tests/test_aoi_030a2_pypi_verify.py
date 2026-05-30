from ai_objective_index import aoi_030a2_pypi_verify as verify


def test_pypi_verify_holds_without_upload():
    result = verify.run_pypi_verify(upload_result={"decision": "HOLD_ENV_CONFIRM_REQUIRED"}, write_result=False)

    assert result["decision"] == "HOLD_PYPI_UPLOAD_NOT_CONFIRMED"


def test_pypi_verify_mocked_success():
    def runner(command, timeout=600):
        if "-c" in command:
            return {"ok": True, "stdout": "0.3.0a2\n", "stderr": "", "command": command}
        return {"ok": True, "stdout": "ok", "stderr": "", "command": command}

    result = verify.run_pypi_verify(
        runner=runner,
        upload_result={"decision": "PASS_PYPI_UPLOAD_COMPLETED"},
        create_venv=lambda path: {"ok": True},
        cleanup_venv=lambda path: True,
        write_result=False,
    )

    assert result["decision"] == "PASS_PYPI_030A2_VERIFIED"
    assert result["token_printed"] is False


def test_pypi_verify_version_mismatch_blocks():
    def runner(command, timeout=600):
        if "-c" in command:
            return {"ok": True, "stdout": "0.3.0a1\n", "stderr": "", "command": command}
        return {"ok": True, "stdout": "ok", "stderr": "", "command": command}

    result = verify.run_pypi_verify(
        runner=runner,
        upload_result={"decision": "PASS_PYPI_UPLOAD_COMPLETED"},
        create_venv=lambda path: {"ok": True},
        cleanup_venv=lambda path: True,
        write_result=False,
    )

    assert result["decision"] == "BLOCK_IMPORT_VERSION_MISMATCH"
