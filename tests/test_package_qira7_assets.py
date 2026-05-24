from pathlib import Path


def test_qira7_docs_and_actions_exist():
    for path in [
        "docs/qira7_github_ci_evidence_bridge.md",
        "docs/qira_github_ci_bridge_limitations.md",
        ".github/actions/qira-ci-evidence-bridge/action.yml",
        "examples/qira_ci_evidence_bridge_workflow.yml",
    ]:
        assert Path(path).exists(), path


def test_qira7_outputs_exist():
    for path in [
        "public_launch/qira7/QIRA7_SAMPLE_TASK_PACKET.json",
        "public_launch/qira7/QIRA7_CI_EVIDENCE.json",
        "public_launch/qira7/QIRA7_VALIDATION_RESULT.json",
        "public_launch/qira7/QIRA7_AUGMENTED_TASK_PACKET.json",
        "public_launch/qira7/QIRA7_REVIEW_RESULT.json",
        "public_launch/qira7/QIRA7_BRIDGE_RESULT.json",
        "public_launch/qira7/QIRA7_ACTION_MANIFEST_AUDIT.json",
        "public_launch/qira7/QIRA7_NEXT_STEPS.md",
        "public_launch/qira7/QIRA_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert Path(path).exists(), path


def test_qira7_does_not_auto_enable_workflow():
    assert not Path(".github/workflows/qira-ci-evidence-bridge.yml").exists()


def test_qira7_docs_preserve_no_api_or_token_boundary():
    text = Path("docs/qira7_github_ci_evidence_bridge.md").read_text(encoding="utf-8")

    assert "does not call GitHub APIs" in text
    assert "does not run project commands on its own" in text
    assert "handle tokens" in text
