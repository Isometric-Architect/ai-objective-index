from ai_objective_index.portfolio.second_run_redaction import scan_second_run_payload


def test_second_run_redaction_blocks_token_like_strings():
    report = scan_second_run_payload("ghp_abcdefghijklmnopqrstuvwxyz0123456789", label="token")
    assert report["decision"] == "BLOCK_SENSITIVE_CONTENT"
