from ai_objective_index.portfolio.pilot_dry_run_redaction import scan_dry_run_payload


def test_dry_run_redaction_blocks_token_like_strings():
    result = scan_dry_run_payload("pypi-abcdefghijklmnopqrstuvwxyz123456", label="fixture")
    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"
