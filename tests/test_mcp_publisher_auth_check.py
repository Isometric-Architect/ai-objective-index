from ai_objective_index import mcp_publisher_auth_check as auth


def test_auth_check_accepts_non_publishing_probe(monkeypatch):
    monkeypatch.setattr(auth, "find_mcp_publisher", lambda: "mcp-publisher")
    monkeypatch.setattr(
        auth,
        "_run_non_publishing_probe",
        lambda command: {"ok": True, "publish_or_validate_can_run": True, "checks": []},
    )

    result = auth.run_mcp_publisher_auth_check(write_result=False)

    assert result["decision"] == "PASS_AUTH_ASSUMED_FROM_DIRECT_LOGIN"
    assert result["auth_available"] is True


def test_auth_check_without_probe_holds(monkeypatch):
    monkeypatch.setattr(auth, "find_mcp_publisher", lambda: "mcp-publisher")
    monkeypatch.setattr(
        auth,
        "_run_non_publishing_probe",
        lambda command: {"ok": False, "publish_or_validate_can_run": False, "checks": []},
    )

    result = auth.run_mcp_publisher_auth_check(write_result=False)

    assert result["decision"] == "HOLD_AUTH_STATUS_NOT_CHECKED"


def test_auth_login_success(monkeypatch):
    monkeypatch.setattr(auth, "find_mcp_publisher", lambda: "mcp-publisher")
    monkeypatch.setattr(auth, "_run_login", lambda command: {"ok": True, "returncode": 0, "stdout": "ok", "stderr": ""})

    result = auth.run_mcp_publisher_auth_check(mode="login", write_result=False)

    assert result["decision"] == "PASS_AUTH_CONFIRMED"
    assert result["login_attempted"] is True


def test_auth_redacts_token_like_output():
    text = auth.redact_token_like("github_pat_abc ghp_abc pypi-abc")

    assert "github_pat_[redacted]" in text
    assert "pypi-[redacted]" in text
