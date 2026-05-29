from pathlib import Path

from ai_objective_index.portfolio import residualops_portfolio_redaction as redaction


def test_portfolio_redaction_blocks_token_like_strings():
    result = redaction.scan_portfolio_payload({"note": "token pypi-abcdefghijklmnopqrstuvwxyz123456"}, "fixture")
    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"


def test_portfolio_redaction_blocks_private_kernel_values():
    result = redaction.scan_portfolio_payload("provider trust prior: 0.91", "fixture")
    assert result["decision"] == "BLOCK_SENSITIVE_CONTENT"


def test_portfolio_redaction_writes_pass_report():
    path = Path("pilot_receipts/portfolio/REDACTION_SAFE_FIXTURE.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("local/offline receipt artifact only\n", encoding="utf-8")
    try:
        result = redaction.scan_portfolio_artifacts([path])
        assert result["decision"] == "PASS_REDACTED"
    finally:
        path.unlink(missing_ok=True)
