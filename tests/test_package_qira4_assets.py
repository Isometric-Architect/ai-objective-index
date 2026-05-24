from pathlib import Path


def test_qira4_docs_and_action_exist():
    for path in [
        "docs/qira4_github_action_dry_run.md",
        "docs/qira_github_action_limitations.md",
        ".github/actions/qira-releasegate-dry-run/action.yml",
        "examples/qira_releasegate_dry_run_workflow.yml",
    ]:
        assert Path(path).exists(), path


def test_qira4_outputs_exist():
    for path in [
        "public_launch/qira4/QIRA4_SAMPLE_ACTION_PACKET.json",
        "public_launch/qira4/QIRA4_GITHUB_ACTION_DRY_RUN_RESULT.json",
        "public_launch/qira4/QIRA4_GITHUB_ACTION_SUMMARY.md",
        "public_launch/qira4/QIRA4_ACTION_MANIFEST_AUDIT.json",
        "public_launch/qira4/QIRA_CLAIM_BOUNDARY_AUDIT.json",
        "public_launch/qira4/QIRA4_NEXT_STEPS.md",
    ]:
        assert Path(path).exists(), path


def test_qira4_does_not_auto_enable_workflow():
    workflow_path = Path(".github/workflows/qira-releasegate-dry-run.yml")

    assert not workflow_path.exists()
