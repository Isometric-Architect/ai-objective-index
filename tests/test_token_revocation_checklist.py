from ai_objective_index.token_revocation_checklist import write_token_revocation_checklist


def test_token_revocation_checklist_mentions_safe_handling():
    path = write_token_revocation_checklist()
    text = path.read_text(encoding="utf-8").lower()

    assert "do not paste" in text
    assert "token" in text
    assert "revoke" in text
    assert "after the switch" in text or "no further hugging face upload" in text
