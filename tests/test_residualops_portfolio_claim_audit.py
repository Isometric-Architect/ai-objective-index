from pathlib import Path

from ai_objective_index.portfolio.residualops_portfolio_claim_audit import run_portfolio_claim_audit
from ai_objective_index.portfolio.residualops_unified_readout import generate_unified_portfolio


def test_portfolio_claim_audit_passes_current_artifacts():
    generate_unified_portfolio(write_result=True)
    result = run_portfolio_claim_audit(write_result=True)
    assert result["decision"] == "PASS_CLAIM_BOUNDARY_CLEAN"
    assert result["risky_phrase_count"] == 0


def test_portfolio_claim_audit_blocks_overclaim_fixture(tmp_path):
    fixture = tmp_path / "claim.md"
    fixture.write_text("This is security certified and production ready.\n", encoding="utf-8")
    result = run_portfolio_claim_audit(paths=[fixture], write_result=False)
    assert result["decision"] == "BLOCK_OVERCLAIM"
