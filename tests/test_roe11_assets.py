from pathlib import Path

from ai_objective_index.portfolio.residualops_unified_readout import generate_unified_portfolio
from ai_objective_index.portfolio.roe11_portfolio_gate import run_roe11_gate


def test_roe11_docs_and_schemas_exist():
    paths = [
        "docs/portfolio/roe11_unified_pilot_receipt_portfolio.md",
        "docs/portfolio/residualops_portfolio_readout.md",
        "docs/portfolio/residualops_vertical_comparison_matrix.md",
        "docs/portfolio/residualops_feedback_memory_index.md",
        "docs/portfolio/residualops_portfolio_claim_boundaries.md",
        "docs/portfolio/residualops_next_pilot_plan.md",
        "schemas/portfolio/residualops_unified_portfolio.schema.json",
        "schemas/portfolio/residualops_vertical_matrix.schema.json",
        "schemas/portfolio/residualops_feedback_memory_index.schema.json",
        "schemas/portfolio/residualops_portfolio_gate.schema.json",
    ]
    for path in paths:
        assert Path(path).exists(), path


def test_roe11_outputs_exist_after_generation():
    generate_unified_portfolio(write_result=True)
    run_roe11_gate(write_result=True)
    paths = [
        "pilot_receipts/portfolio/RESIDUALOPS_UNIFIED_PILOT_PORTFOLIO.json",
        "pilot_receipts/portfolio/RESIDUALOPS_VERTICAL_COMPARISON_MATRIX.json",
        "pilot_receipts/portfolio/RESIDUALOPS_VERTICAL_COMPARISON_MATRIX.md",
        "pilot_receipts/portfolio/RESIDUALOPS_FEEDBACK_MEMORY_INDEX.json",
        "pilot_receipts/portfolio/RESIDUALOPS_PORTFOLIO_REVIEWER_READOUT.md",
        "pilot_receipts/portfolio/RESIDUALOPS_PORTFOLIO_CLAIM_BOUNDARY.md",
        "pilot_receipts/portfolio/RESIDUALOPS_PORTFOLIO_REDACTION_REPORT.json",
        "pilot_receipts/portfolio/RESIDUALOPS_PORTFOLIO_KNOWN_LIMITS.md",
        "pilot_receipts/portfolio/RESIDUALOPS_NEXT_PILOT_PLAN.md",
        "public_launch/roe11/ROE11_PORTFOLIO_CLAIM_AUDIT.json",
        "public_launch/roe11/ROE11_UNIFIED_PORTFOLIO_GATE_RESULT.json",
        "public_launch/roe11/ROE11_UNIFIED_PORTFOLIO_SUMMARY.md",
        "public_launch/roe11/ROE11_NEXT_ACTIONS.md",
    ]
    for path in paths:
        assert Path(path).exists(), path
