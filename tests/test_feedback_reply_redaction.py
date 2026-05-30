from ai_objective_index.portfolio.feedback_reply_redaction import build_redaction_report, redact_reply_text, scan_feedback_reply_text


def test_redaction_blocks_token_like_strings():
    findings = scan_feedback_reply_text("token is ghp_abcdefghijklmnopqrstuvwxyz123456")
    report = build_redaction_report(findings)
    assert report["decision"] == "BLOCK_SENSITIVE_CONTENT"


def test_redact_reply_text_replaces_secret():
    redacted, findings = redact_reply_text("token is sk-abcdefghijklmnopqrstuvwxyz123456")
    assert findings
    assert "[REDACTED]" in redacted
