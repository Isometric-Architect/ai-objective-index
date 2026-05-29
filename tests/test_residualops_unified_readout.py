from pathlib import Path

from ai_objective_index.portfolio.residualops_unified_readout import generate_unified_portfolio


def test_unified_readout_generates_three_verticals():
    result = generate_unified_portfolio(write_result=True)
    portfolio = result["portfolio"]
    assert portfolio["portfolio_summary"]["vertical_count"] == 3
    assert portfolio["portfolio_summary"]["total_allow_count"] == 3
    assert portfolio["portfolio_summary"]["total_hold_count"] == 3
    assert portfolio["portfolio_summary"]["total_block_count"] == 3
    assert result["redaction"]["decision"] == "PASS_REDACTED"
    assert Path("pilot_receipts/portfolio/RESIDUALOPS_PORTFOLIO_REVIEWER_READOUT.md").exists()


def test_reviewer_readout_mentions_all_verticals():
    generate_unified_portfolio(write_result=True)
    text = Path("pilot_receipts/portfolio/RESIDUALOPS_PORTFOLIO_REVIEWER_READOUT.md").read_text(encoding="utf-8")
    assert "AgentSec Gate" in text
    assert "QIRA-Code ReleaseGate" in text
    assert "DataCapsule / AIDREG Engine" in text
    assert "Not security certification" in text
