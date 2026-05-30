from ai_objective_index import aoi_mcp_registry_recovery_publish as publish


def test_recovery_publish_requires_env(monkeypatch):
    monkeypatch.setattr(publish, "_read_gate", lambda: {"decision": "PASS_READY_FOR_MCP_REGISTRY_RECOVERY_PUBLISH"})

    result = publish.run_recovery_publish(env={}, publisher_finder=lambda: "mcp-publisher", write_result=False)

    assert result["decision"] == "HOLD_ENV_CONFIRM_REQUIRED"
    assert result["submission_performed"] is False


def test_recovery_publish_holds_when_gate_not_pass(monkeypatch):
    monkeypatch.setattr(publish, "_read_gate", lambda: {"decision": "HOLD_PYPI_VERIFY_REQUIRED"})

    result = publish.run_recovery_publish(
        env={publish.CONFIRM_ENV: "YES"},
        publisher_finder=lambda: "mcp-publisher",
        write_result=False,
    )

    assert result["decision"] == "HOLD_GATE_NOT_PASS"


def test_recovery_publish_mocked_success(monkeypatch):
    monkeypatch.setattr(publish, "_read_gate", lambda: {"decision": "PASS_READY_FOR_MCP_REGISTRY_RECOVERY_PUBLISH"})

    result = publish.run_recovery_publish(
        env={publish.CONFIRM_ENV: "YES"},
        publisher_finder=lambda: "mcp-publisher",
        runner=lambda command, timeout=300: {"ok": True, "returncode": 0, "stdout": "ok", "stderr": ""},
        write_result=False,
    )

    assert result["decision"] == "PASS_MCP_REGISTRY_RECOVERY_PUBLISHED"
    assert result["submission_performed"] is True
