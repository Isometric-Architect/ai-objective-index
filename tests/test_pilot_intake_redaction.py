from ai_objective_index.portfolio.pilot_intake_redaction import scan_intake_payload


def test_redaction_blocks_token_like_strings():
    result = scan_intake_payload("token: pypi-abcdefghijklmnopqrstuvwxyz123456", label="fixture")
    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"


def test_redaction_holds_pii_dataset_rows():
    result = scan_intake_payload("name,email,phone\nAlice,alice@example.com,555-111-2222", label="fixture")
    assert result["decision"] in {"HOLD_REVIEW_RECOMMENDED", "BLOCK_SENSITIVE_CONTENT"}
    assert result["finding_count"] > 0
