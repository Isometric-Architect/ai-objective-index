from pathlib import Path

from ai_objective_index.qira.optional_workflow_artifact import build_qira9_optional_workflow_artifact


ROOT = Path(__file__).resolve().parents[1]


def test_qira9_docs_exist():
    for relative in [
        "docs/qira9_optional_workflow_artifact.md",
        "docs/qira_workflow_opt_in_runbook.md",
        "docs/qira_workflow_artifact_limitations.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_qira9_outputs_exist_after_generation():
    build_qira9_optional_workflow_artifact(write_result=True)

    for relative in [
        "examples/qira9_optional_pr_review_artifact_workflow.yml",
        "public_launch/qira9/QIRA9_OPTIONAL_WORKFLOW_RESULT.json",
        "public_launch/qira9/QIRA9_WORKFLOW_AUDIT.json",
        "public_launch/qira9/QIRA9_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/qira9/QIRA9_ARTIFACT_MANIFEST.json",
        "public_launch/qira9/QIRA9_OPERATOR_RUNBOOK.md",
        "public_launch/qira9/QIRA9_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_qira9_no_active_workflow_created():
    build_qira9_optional_workflow_artifact(write_result=True)

    assert not (ROOT / ".github/workflows/qira9-optional-pr-review-artifact.yml").exists()
    text = (ROOT / "public_launch/qira9/QIRA9_OPERATOR_RUNBOOK.md").read_text(encoding="utf-8")
    assert "not active" in text
    assert "does not post comments" in text
