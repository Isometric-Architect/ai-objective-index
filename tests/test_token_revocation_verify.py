from ai_objective_index.token_revocation_verify import run_token_revocation_verify


def test_token_revocation_verify_does_not_print_token_and_handles_auth_failure():
    def fake_auth_checker(**_kwargs):
        return {"authenticated": False, "token_printed": False}

    result = run_token_revocation_verify(auth_checker=fake_auth_checker, write_result=False)

    assert result["token_printed"] is False
    assert result["token_committed"] is False
    assert result["hf_auth_available"] is False
    assert any("Delete/Revoke" in step for step in result["manual_steps"])

