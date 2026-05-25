from pathlib import Path

from ai_objective_index.agentsec.optional_workflow_artifact import build_agentsec8_optional_workflow_artifact


ROOT = Path(__file__).resolve().parents[1]


def test_agentsec8_docs_exist():
    for relative in [
        "docs/agentsec8_optional_workflow_artifact.md",
        "docs/agentsec_workflow_opt_in_runbook.md",
        "docs/agentsec_workflow_artifact_limitations.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_agentsec8_outputs_exist_after_generation():
    build_agentsec8_optional_workflow_artifact(write_result=True)

    for relative in [
        "examples/agentsec8_optional_pr_review_artifact_workflow.yml",
        "public_launch/agentsec8/AGENTSEC8_OPTIONAL_WORKFLOW_RESULT.json",
        "public_launch/agentsec8/AGENTSEC8_WORKFLOW_AUDIT.json",
        "public_launch/agentsec8/AGENTSEC8_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/agentsec8/AGENTSEC8_ARTIFACT_MANIFEST.json",
        "public_launch/agentsec8/AGENTSEC8_OPERATOR_RUNBOOK.md",
        "public_launch/agentsec8/AGENTSEC8_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_agentsec8_no_active_workflow_created():
    build_agentsec8_optional_workflow_artifact(write_result=True)

    assert not (ROOT / ".github/workflows/agentsec8-optional-pr-review-artifact.yml").exists()
    text = (ROOT / "public_launch/agentsec8/AGENTSEC8_OPERATOR_RUNBOOK.md").read_text(encoding="utf-8")
    assert "not active" in text
    assert "does not post comments" in text
