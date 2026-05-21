from ai_objective_index import mcp_registry_publish_runner as runner


def _patch_ready(monkeypatch, publisher=True):
    monkeypatch.setattr(runner, "run_mcp_publisher_setup", lambda write_result=False: {"decision": "PASS_MCP_PUBLISHER_AVAILABLE"})
    monkeypatch.setattr(runner, "run_mcp_registry_manifest_final_audit", lambda write_result=False: {"decision": "PASS_MANIFEST_READY"})
    monkeypatch.setattr(runner.shutil, "which", lambda name: "mcp-publisher" if publisher else None)


def test_publish_runner_dry_run_does_not_publish(monkeypatch):
    _patch_ready(monkeypatch)

    result = runner.run_mcp_registry_publish_runner(mode="dry-run", write_result=False)

    assert result["result_token"] == "DRY_RUN_ONLY"
    assert result["submission_performed"] is False


def test_publish_runner_login_mocked(monkeypatch):
    _patch_ready(monkeypatch)
    monkeypatch.setattr(runner, "_run_command", lambda command, timeout=240: {"ok": True, "returncode": 0, "stdout": "", "stderr": ""})

    result = runner.run_mcp_registry_publish_runner(mode="login", write_result=False)

    assert result["result_token"] == "LOGIN_SUCCESS"
    assert result["login_attempted"] is True


def test_publish_runner_execute_without_env_refuses(monkeypatch):
    _patch_ready(monkeypatch)

    result = runner.run_mcp_registry_publish_runner(mode="execute", env={}, write_result=False)

    assert result["result_token"] == "HOLD_ENV_CONFIRM_REQUIRED"
    assert result["submission_performed"] is False


def test_publish_runner_execute_success(monkeypatch):
    _patch_ready(monkeypatch)
    monkeypatch.setattr(runner, "_run_command", lambda command, timeout=300: {"ok": True, "returncode": 0, "stdout": "ok", "stderr": ""})

    result = runner.run_mcp_registry_publish_runner(
        mode="execute",
        env={runner.CONFIRM_ENV: "YES"},
        write_result=False,
    )

    assert result["result_token"] == "PUBLISH_SUCCESS"
    assert result["submission_performed"] is True


def test_publish_runner_redacts_tokens():
    text = runner.redact_token_like("github_pat_abc pypi-abc ghp_abc hf_abc")

    assert "github_pat_[redacted]" in text
    assert "pypi-[redacted]" in text
