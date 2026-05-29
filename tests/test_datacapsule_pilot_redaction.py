from ai_objective_index.portfolio.datacapsule_pilot_redaction import scan_payload


def test_datacapsule_redaction_passes_safe_payload():
    result = scan_payload({"note": "local manifest metadata only"})

    assert result["decision"] == "PASS_REDACTED"


def test_datacapsule_redaction_blocks_token_like_payload():
    result = scan_payload({"note": "token = pypi-abcdefghijklmnopqrstuvwxyz123456"})

    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"


def test_datacapsule_redaction_blocks_pii_like_raw_rows():
    result = scan_payload({"raw_row": "person@example.com,555-123-4567"})

    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"
