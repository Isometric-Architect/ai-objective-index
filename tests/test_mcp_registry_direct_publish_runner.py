from ai_objective_index import mcp_registry_direct_publish_runner as runner


def _validate(ok=True):
    return {
        "decision": "PASS_VALIDATE" if ok else "BLOCK_VALIDATE_FAILED",
        "validate_ok": ok,
        "validate_result": {"ok": ok, "returncode": 0 if ok else 1, "stdout": "valid" if ok else "", "stderr": ""},
    }


def test_direct_publish_refuses_without_env(monkeypatch):
    monkeypatch.setattr(runner, "find_mcp_publisher", lambda: "tools/mcp-publisher/mcp-publisher.exe")
    monkeypatch.setattr(runner, "validate_server_json", lambda publisher=None, write_result=True: _validate(True))
    monkeypatch.setattr(runner, "run_mcp_registry_publish_preflight", lambda write_result=True: {"decision": "PASS_READY_TO_SUBMIT"})
    monkeypatch.setattr(runner, "_read_json", lambda path: {"decision": "PASS_AUTH_CONFIRMED"})

    result = runner.run_mcp_registry_direct_publish(execute=True, env={}, write_result=False)

    assert result["result_token"] == "HOLD_ENV_CONFIRM_REQUIRED"
    assert result["publish_attempted"] is False


def test_direct_publish_overrides_auth_status_unknown_with_env_and_validate(monkeypatch):
    commands = []
    monkeypatch.setattr(runner, "find_mcp_publisher", lambda: "tools/mcp-publisher/mcp-publisher.exe")
    monkeypatch.setattr(runner, "validate_server_json", lambda publisher=None, write_result=True: _validate(True))
    monkeypatch.setattr(runner, "run_mcp_registry_publish_preflight", lambda write_result=True: {"decision": "HOLD_AUTH_STATUS_NOT_CHECKED"})
    monkeypatch.setattr(runner, "_read_json", lambda path: {"decision": "HOLD_AUTH_STATUS_NOT_CHECKED"})

    def fake_run(command, timeout=180):
        commands.append(command)
        return {"ok": False, "returncode": 1, "stdout": "", "stderr": "You must be logged in", "command_redacted": " ".join(command)}

    monkeypatch.setattr(runner, "_run_publisher_command", fake_run)

    result = runner.run_mcp_registry_direct_publish(
        execute=True,
        env={runner.CONFIRM_ENV: "YES"},
        write_result=False,
    )

    assert result["result_token"] == "BLOCK_PUBLISH_FAILED"
    assert result["failure_classification"] == "AUTH_REQUIRED"
    assert result["publish_attempted"] is True
    assert commands[0][1] == "publish"


def test_direct_publish_success_records_submission(monkeypatch):
    monkeypatch.setattr(runner, "find_mcp_publisher", lambda: "tools/mcp-publisher/mcp-publisher.exe")
    monkeypatch.setattr(runner, "validate_server_json", lambda publisher=None, write_result=True: _validate(True))
    monkeypatch.setattr(runner, "run_mcp_registry_publish_preflight", lambda write_result=True: {"decision": "PASS_READY_TO_SUBMIT"})
    monkeypatch.setattr(runner, "_read_json", lambda path: {"decision": "PASS_AUTH_CONFIRMED"})
    monkeypatch.setattr(
        runner,
        "_run_publisher_command",
        lambda command, timeout=180: {"ok": True, "returncode": 0, "stdout": "published", "stderr": "", "command_redacted": " ".join(command)},
    )

    result = runner.run_mcp_registry_direct_publish(
        execute=True,
        env={runner.CONFIRM_ENV: "YES"},
        write_result=False,
    )

    assert result["result_token"] == "PUBLISH_SUCCESS"
    assert result["submission_performed"] is True
