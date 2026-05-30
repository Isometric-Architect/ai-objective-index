from ai_objective_index.portfolio.feedback_second_run_redaction import build_redaction_report, scan_text


def test_feedback_second_run_redaction_blocks_token_like_strings():
    findings = scan_text("token = sk-abcdefghijklmnopqrstuvwxyz123456", "fixture")
    report = build_redaction_report(findings, artifact_count=1)
    assert report["decision"] == "BLOCK_SENSITIVE_CONTENT"
    assert report["block_count"] == 1
