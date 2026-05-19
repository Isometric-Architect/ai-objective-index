import ai_objective_index.hf_auth_check as auth


def test_hf_auth_check_unauthenticated_safe(monkeypatch):
    monkeypatch.setattr(auth, "_package_available", lambda: False)
    monkeypatch.setattr(auth, "_cli_candidates", lambda: [])

    result = auth.check_hf_auth(write_result=False)

    assert result["hf_package_available"] is False
    assert result["authenticated"] is False
    assert result["token_printed"] is False
    assert "Do not paste tokens" in result["recommended_next_action"]


def test_hf_auth_check_cli_authenticated(monkeypatch):
    monkeypatch.setattr(auth, "_package_available", lambda: False)
    monkeypatch.setattr(auth, "_cli_candidates", lambda: [["hf", "auth", "whoami"]])

    result = auth.check_hf_auth(
        command_runner=lambda _cmd: {"ok": True, "stdout": "edict-lab", "stderr": ""},
        write_result=False,
    )

    assert result["authenticated"] is True
    assert result["username_if_known"] == "edict-lab"
    assert result["token_printed"] is False

