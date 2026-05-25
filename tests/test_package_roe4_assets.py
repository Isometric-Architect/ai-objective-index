from pathlib import Path

from ai_objective_index.residualops_distribution_gate import run_distribution_split_gate


ROOT = Path(__file__).resolve().parents[1]


def test_roe4_docs_exist():
    for relative in [
        "docs/roe4_public_private_distribution_split.md",
        "docs/residualops_opt_in_workflow_distribution_runbook.md",
        "docs/residualops_distribution_limitations.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe4_outputs_exist_after_generation():
    run_distribution_split_gate(write_result=True)

    for relative in [
        "public_launch/roe4/ROE4_DISTRIBUTION_SPLIT_GATE.json",
        "public_launch/roe4/ROE4_PUBLIC_PRIVATE_DISTRIBUTION_MATRIX.json",
        "public_launch/roe4/ROE4_OPT_IN_WORKFLOW_DISTRIBUTION_RUNBOOK.md",
        "public_launch/roe4/ROE4_PORTFOLIO_DISTRIBUTION_SUMMARY.md",
        "public_launch/roe4/ROE4_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/roe4/ROE4_ARTIFACT_MANIFEST.json",
        "public_launch/roe4/ROE4_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_roe4_summary_preserves_boundaries():
    run_distribution_split_gate(write_result=True)
    text = (ROOT / "public_launch/roe4/ROE4_PORTFOLIO_DISTRIBUTION_SUMMARY.md").read_text(encoding="utf-8")

    assert "not verification" in text
    assert "authorization for actions" in text
