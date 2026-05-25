from pathlib import Path

from ai_objective_index.datacapsule.optional_workflow_artifact import build_datacapsule7_optional_workflow_artifact


ROOT = Path(__file__).resolve().parents[1]


def test_datacapsule7_docs_exist():
    for relative in [
        "docs/datacapsule7_optional_workflow_artifact.md",
        "docs/datacapsule_workflow_opt_in_runbook.md",
        "docs/datacapsule_workflow_artifact_limitations.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_datacapsule7_outputs_exist_after_generation():
    build_datacapsule7_optional_workflow_artifact(write_result=True)

    for relative in [
        "examples/datacapsule7_repository_manifest_workflow.yml",
        "public_launch/datacapsule7/DATACAPSULE7_OPTIONAL_WORKFLOW_RESULT.json",
        "public_launch/datacapsule7/DATACAPSULE7_WORKFLOW_AUDIT.json",
        "public_launch/datacapsule7/DATACAPSULE7_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/datacapsule7/DATACAPSULE7_ARTIFACT_MANIFEST.json",
        "public_launch/datacapsule7/DATACAPSULE7_OPERATOR_RUNBOOK.md",
        "public_launch/datacapsule7/DATACAPSULE7_NEXT_STEPS.md",
    ]:
        assert (ROOT / relative).exists(), relative


def test_datacapsule7_no_active_workflow_created():
    build_datacapsule7_optional_workflow_artifact(write_result=True)

    assert not (ROOT / ".github/workflows/datacapsule7-repository-manifest-artifact.yml").exists()
    text = (ROOT / "public_launch/datacapsule7/DATACAPSULE7_OPERATOR_RUNBOOK.md").read_text(encoding="utf-8")
    assert "not active" in text
    assert "does not post comments" in text
