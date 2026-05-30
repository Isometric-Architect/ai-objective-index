from ai_objective_index.portfolio.dashboard_refresh_redaction import build_redaction_report, scan_text


def test_dashboard_refresh_redaction_blocks_token_like_strings():
    findings = scan_text("token pypi-abcdefghijklmnopqrstuvwxyz123456", "fixture")
    report = build_redaction_report(findings, artifact_count=1)
    assert report["decision"] == "BLOCK_SENSITIVE_CONTENT"
    assert report["finding_count"] == 1
