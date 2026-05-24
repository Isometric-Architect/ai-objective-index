from pathlib import Path


def test_qira6_docs_exist():
    for path in [
        "docs/qira6_ci_evidence_intake.md",
        "docs/qira_ci_evidence_limitations.md",
    ]:
        assert Path(path).exists(), path


def test_qira6_outputs_exist():
    for path in [
        "public_launch/qira6/QIRA6_SAMPLE_TASK_PACKET.json",
        "public_launch/qira6/QIRA6_SAMPLE_CI_EVIDENCE.json",
        "public_launch/qira6/QIRA6_VALIDATION_RESULT.json",
        "public_launch/qira6/QIRA6_AUGMENTED_TASK_PACKET.json",
        "public_launch/qira6/QIRA6_REVIEW_RESULT.json",
        "public_launch/qira6/QIRA6_NEXT_STEPS.md",
        "public_launch/qira6/QIRA_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert Path(path).exists(), path


def test_qira6_docs_preserve_no_execution_boundary():
    text = Path("docs/qira6_ci_evidence_intake.md").read_text(encoding="utf-8")

    assert "does not run tests" in text
    assert "does not call GitHub APIs" in text
    assert "does not authorize merge" in text
