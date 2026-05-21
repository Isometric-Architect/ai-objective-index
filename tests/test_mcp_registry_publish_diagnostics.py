from ai_objective_index import mcp_registry_publish_diagnostics as diagnostics


def test_validate_uses_local_publisher(monkeypatch):
    monkeypatch.setattr(diagnostics, "find_mcp_publisher", lambda: "tools/mcp-publisher/mcp-publisher.exe")
    monkeypatch.setattr(
        diagnostics,
        "_run_publisher_command",
        lambda command, timeout=180: {
            "ok": True,
            "returncode": 0,
            "stdout": "valid",
            "stderr": "",
            "command_redacted": " ".join(command),
            "token_printed": False,
        },
    )

    result = diagnostics.validate_server_json(write_result=False)

    assert result["decision"] == "PASS_VALIDATE"
    assert result["mcp_publisher_path"].endswith("mcp-publisher.exe")
    assert "validate" in result["validate_command"]


def test_diagnostics_classifies_validate_failure(monkeypatch):
    monkeypatch.setattr(diagnostics, "find_mcp_publisher", lambda: "tools/mcp-publisher/mcp-publisher.exe")
    monkeypatch.setattr(
        diagnostics,
        "_run_publisher_command",
        lambda command, timeout=180: {
            "ok": False,
            "returncode": 1,
            "stdout": "",
            "stderr": "validation failed: server returned status 422",
            "command_redacted": " ".join(command),
            "token_printed": False,
        },
    )

    result = diagnostics.run_mcp_registry_publish_diagnostics(write_result=False)

    assert result["validate"]["decision"] == "BLOCK_VALIDATE_FAILED"
    assert result["classification"]["classification"] == "SERVER_JSON_INVALID"


def test_diagnostics_classifies_latest_publish_failure(monkeypatch):
    monkeypatch.setattr(diagnostics, "find_mcp_publisher", lambda: "tools/mcp-publisher/mcp-publisher.exe")
    monkeypatch.setattr(
        diagnostics,
        "_run_publisher_command",
        lambda command, timeout=180: {
            "ok": True,
            "returncode": 0,
            "stdout": "valid",
            "stderr": "",
            "command_redacted": " ".join(command),
            "token_printed": False,
        },
    )
    monkeypatch.setattr(
        diagnostics,
        "_read_json",
        lambda path: {
            "execute": True,
            "result_token": "BLOCK_PUBLISH_FAILED",
            "publish_result": {"ok": False, "returncode": 1, "stdout": "", "stderr": "status 401: Unauthorized"},
        },
    )

    result = diagnostics.run_mcp_registry_publish_diagnostics(write_result=False)

    assert result["publish_attempted"] is True
    assert result["classification"]["classification"] == "AUTH_REQUIRED"
