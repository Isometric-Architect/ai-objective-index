from ai_objective_index.portfolio.pilot_feedback_redaction import scan_feedback_payload


def test_feedback_redaction_blocks_token_like_strings():
    report = scan_feedback_payload("pypi-abcdefghijklmnopqrstuvwxyz012345", label="token-fixture")
    assert report["decision"] == "BLOCK_SENSITIVE_CONTENT"


def test_feedback_redaction_blocks_raw_pii_rows():
    report = scan_feedback_payload("name,email,address\nJane,jane@example.com,1 Main St", label="pii-fixture")
    assert report["decision"] == "BLOCK_SENSITIVE_CONTENT"
