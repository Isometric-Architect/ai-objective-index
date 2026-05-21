from ai_objective_index import real_pypi_install_verify


def test_real_pypi_install_verify_mocked_success():
    def runner(command, timeout=600):
        if "-c" in command:
            return {"ok": True, "stdout": "0.3.0a1\n", "stderr": "", "command": command}
        return {"ok": True, "stdout": "ok", "stderr": "", "command": command}

    result = real_pypi_install_verify.run_real_pypi_install_verify(
        runner=runner,
        upload_result={"result_token": "UPLOAD_SUCCESS"},
        create_venv=lambda path: {"ok": True},
        cleanup_venv=lambda path: True,
        write_result=False,
    )

    assert result["decision"] == "PASS_REAL_PYPI_INSTALL"
    assert result["external_api_keys_required"] is False


def test_real_pypi_install_verify_import_failure_blocks():
    def runner(command, timeout=600):
        if "-c" in command:
            return {"ok": False, "stdout": "", "stderr": "import failed", "command": command}
        return {"ok": True, "stdout": "ok", "stderr": "", "command": command}

    result = real_pypi_install_verify.run_real_pypi_install_verify(
        runner=runner,
        upload_result={"result_token": "UPLOAD_SUCCESS"},
        create_venv=lambda path: {"ok": True},
        cleanup_venv=lambda path: True,
        write_result=False,
    )

    assert result["decision"] == "BLOCK_IMPORT_FAILED"


def test_real_pypi_install_verify_not_attempted_before_upload():
    result = real_pypi_install_verify.run_real_pypi_install_verify(
        upload_result={"result_token": "DRY_RUN_ONLY"},
        create_venv=lambda path: {"ok": True},
        write_result=False,
    )

    assert result["decision"] == "HOLD_PYPI_PACKAGE_NOT_FOUND"
