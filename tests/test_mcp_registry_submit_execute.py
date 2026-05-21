from ai_objective_index import mcp_registry_submit_execute as submit


def test_submit_dry_run_does_not_publish(monkeypatch):
    monkeypatch.setattr(submit, "run_mcp_registry_publish_preflight", lambda write_result=False: {"decision": "PASS_READY_TO_SUBMIT"})
    monkeypatch.setattr(submit, "find_mcp_publisher", lambda: "")

    result = submit.run_mcp_registry_submit_execute(write_result=False)

    assert result["result_token"] == "DRY_RUN_ONLY"
    assert result["submission_performed"] is False


def test_submit_execute_without_env_refuses(monkeypatch):
    monkeypatch.setattr(submit, "run_mcp_registry_publish_preflight", lambda write_result=False: {"decision": "PASS_READY_TO_SUBMIT"})
    monkeypatch.setattr(submit, "find_mcp_publisher", lambda: "mcp-publisher")

    result = submit.run_mcp_registry_submit_execute(execute=True, env={}, write_result=False)

    assert result["result_token"] == "HOLD_ENV_CONFIRM_REQUIRED"


def test_submit_execute_mocked_success(monkeypatch):
    monkeypatch.setattr(submit, "run_mcp_registry_publish_preflight", lambda write_result=False: {"decision": "PASS_READY_TO_SUBMIT"})
    monkeypatch.setattr(submit, "find_mcp_publisher", lambda: "mcp-publisher")
    monkeypatch.setattr(submit, "_run_command", lambda command, timeout=300: {"ok": True, "returncode": 0, "stdout": "ok", "stderr": ""})

    result = submit.run_mcp_registry_submit_execute(
        execute=True,
        env={submit.CONFIRM_ENV: "YES"},
        write_result=False,
    )

    assert result["result_token"] == "PUBLISH_SUCCESS"
    assert result["submission_performed"] is True


def test_submit_already_published_holds(monkeypatch):
    monkeypatch.setattr(submit, "run_mcp_registry_publish_preflight", lambda write_result=False: {"decision": "PASS_READY_TO_SUBMIT"})
    monkeypatch.setattr(submit, "find_mcp_publisher", lambda: "mcp-publisher")
    monkeypatch.setattr(submit, "_run_command", lambda command, timeout=300: {"ok": False, "returncode": 1, "stdout": "already exists", "stderr": ""})

    result = submit.run_mcp_registry_submit_execute(
        execute=True,
        env={submit.CONFIRM_ENV: "YES"},
        write_result=False,
    )

    assert result["result_token"] == "HOLD_ALREADY_PUBLISHED_OR_VERSION_EXISTS"


def test_submit_token_redaction():
    text = submit.redact_token_like("ghp_abc pypi-abc")

    assert "ghp_[redacted]" in text
