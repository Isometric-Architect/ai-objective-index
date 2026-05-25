from pathlib import Path

from ai_objective_index.agentsec.reviewer_bundle import build_agentsec7_bundle
from ai_objective_index.agentsec_claim_audit import run_agentsec_claim_audit


ROOT = Path(__file__).resolve().parents[1]


def test_agentsec7_docs_exist():
    for relative in [
        "docs/agentsec7_pr_artifact_bundle.md",
        "docs/agentsec_reviewer_report_limitations.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_agentsec7_outputs_exist_after_generation():
    build_agentsec7_bundle(run_upstream_sample=True)
    run_agentsec_claim_audit(write_result=True)

    for relative in [
        "public_launch/agentsec7/AGENTSEC7_REVIEWER_REPORT.md",
        "public_launch/agentsec7/AGENTSEC7_PR_COMMENT_DRAFT.md",
        "public_launch/agentsec7/AGENTSEC7_ARTIFACT_MANIFEST.json",
        "public_launch/agentsec7/AGENTSEC7_BUNDLE_RESULT.json",
        "public_launch/agentsec7/AGENTSEC7_NEXT_STEPS.md",
        "public_launch/agentsec7/AGENTSEC_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert (ROOT / relative).exists(), relative


def test_agentsec7_report_does_not_post_comment():
    build_agentsec7_bundle(run_upstream_sample=True)
    text = (ROOT / "public_launch/agentsec7/AGENTSEC7_PR_COMMENT_DRAFT.md").read_text(encoding="utf-8")
    report = (ROOT / "public_launch/agentsec7/AGENTSEC7_REVIEWER_REPORT.md").read_text(encoding="utf-8")

    assert "draft only" in text
    assert "PR comment posted | `False`" in report
    assert "call live MCP servers" in text
