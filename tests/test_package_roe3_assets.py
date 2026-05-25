from pathlib import Path

from ai_objective_index.residualops_portfolio_release_audit import run_portfolio_release_audit
from ai_objective_index.residualops_portfolio_release_kit import run_portfolio_release_kit


ROOT = Path(__file__).resolve().parents[1]


def test_roe3_docs_exist():
    for relative in [
        "docs/roe3_unified_portfolio_release_kit.md",
        "docs/residualops_portfolio_handoff.md",
        "docs/residualops_public_claim_boundaries.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe3_outputs_exist_after_generation():
    run_portfolio_release_kit(write_result=True)
    run_portfolio_release_audit(write_result=True)

    for relative in [
        "public_launch/roe3/ROE3_PORTFOLIO_RELEASE_KIT.json",
        "public_launch/roe3/ROE3_PORTFOLIO_RELEASE_NOTES.md",
        "public_launch/roe3/ROE3_PUBLIC_VERTICAL_INDEX.md",
        "public_launch/roe3/ROE3_OPERATOR_HANDOFF.md",
        "public_launch/roe3/ROE3_ARTIFACT_MANIFEST.json",
        "public_launch/roe3/ROE3_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/roe3/ROE3_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe3_release_notes_boundary_text():
    run_portfolio_release_kit(write_result=True)
    text = (ROOT / "public_launch/roe3/ROE3_PORTFOLIO_RELEASE_NOTES.md").read_text(encoding="utf-8")

    assert "does not enable workflows" in text
    assert "authorize actions" in text
