from ai_objective_index.portfolio.qira_pilot_redaction import scan_payload


def test_qira_redaction_passes_safe_payload():
    result = scan_payload({"note": "local qira receipt only"})

    assert result["decision"] == "PASS_REDACTED"


def test_qira_redaction_blocks_token_like_payload():
    result = scan_payload({"note": "token = pypi-abcdefghijklmnopqrstuvwxyz123456"})

    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"


def test_qira_redaction_blocks_private_key_material():
    result = scan_payload({"note": "-----BEGIN PRIVATE KEY----- sample"})

    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"
