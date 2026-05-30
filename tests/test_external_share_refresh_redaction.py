from ai_objective_index.portfolio.external_share_refresh_redaction import build_redaction_report, scan_refresh_payload


def test_external_share_refresh_redaction_blocks_token_like_strings():
    result = scan_refresh_payload("pypi-abcdefghijklmnopqrstuvwxyz123456", label="fixture")
    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"


def test_external_share_refresh_redaction_report_passes_empty():
    result = build_redaction_report([], artifact_count=1)
    assert result["decision"] == "PASS_REDACTED"
