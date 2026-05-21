from ai_objective_index import real_pypi_upload_runner


def test_real_pypi_upload_runner_dry_run_does_not_upload(monkeypatch):
    monkeypatch.setattr(real_pypi_upload_runner, "_read_json", lambda path: {"decision": "PASS_READY_FOR_REAL_PYPI_UPLOAD"})
    result = real_pypi_upload_runner.run_real_pypi_upload(execute=False, write_result=False)

    assert result["result_token"] == "DRY_RUN_ONLY"
    assert result["upload_performed"] is False
    assert "twine upload" in result["command_redacted"]


def test_real_pypi_upload_runner_execute_without_env_refuses(monkeypatch):
    monkeypatch.setattr(real_pypi_upload_runner, "_read_json", lambda path: {"decision": "PASS_READY_FOR_REAL_PYPI_UPLOAD"})
    result = real_pypi_upload_runner.run_real_pypi_upload(
        execute=True,
        env={},
        runner=lambda command, timeout=900: {"ok": True},
        write_result=False,
    )

    assert result["result_token"] == "HOLD_ENV_CONFIRM_REQUIRED"
    assert result["upload_performed"] is False


def test_real_pypi_upload_runner_execute_mocked_uses_no_token_flags(monkeypatch):
    commands = []
    monkeypatch.setattr(real_pypi_upload_runner, "_read_json", lambda path: {"decision": "PASS_READY_FOR_REAL_PYPI_UPLOAD"})

    def runner(command, timeout=900):
        commands.append(command)
        return {"ok": True, "stdout": "uploaded", "stderr": "", "returncode": 0}

    result = real_pypi_upload_runner.run_real_pypi_upload(
        execute=True,
        env={"AOI_REAL_PYPI_UPLOAD_CONFIRM": "YES"},
        runner=runner,
        write_result=False,
    )

    assert result["result_token"] == "UPLOAD_SUCCESS"
    assert result["upload_performed"] is True
    assert commands
    flat = " ".join(commands[0])
    assert "--username" not in flat
    assert "--password" not in flat
    assert "-u" not in commands[0]
    assert "-p" not in commands[0]
    assert result["token_printed"] is False


def test_real_pypi_upload_runner_redacts_token_and_holds_existing(monkeypatch):
    monkeypatch.setattr(real_pypi_upload_runner, "_read_json", lambda path: {"decision": "PASS_READY_FOR_REAL_PYPI_UPLOAD"})

    def runner(command, timeout=900):
        return {"ok": False, "stdout": "File already exists pypi-secret-token-value-1234567890", "stderr": "", "returncode": 1}

    result = real_pypi_upload_runner.run_real_pypi_upload(
        execute=True,
        env={"AOI_REAL_PYPI_UPLOAD_CONFIRM": "YES"},
        runner=runner,
        write_result=False,
    )

    assert result["result_token"] == "HOLD_ALREADY_EXISTS"
    assert "pypi-secret-token-value-1234567890" not in str(result)
