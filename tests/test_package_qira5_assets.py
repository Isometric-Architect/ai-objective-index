from pathlib import Path


def test_qira5_docs_exist():
    for path in [
        "docs/qira5_pr_packet_generator.md",
        "docs/qira_pr_diff_packet_limitations.md",
    ]:
        assert Path(path).exists(), path


def test_qira5_outputs_exist():
    for path in [
        "public_launch/qira5/QIRA5_SAMPLE_PR_DIFF.patch",
        "public_launch/qira5/QIRA5_GENERATED_TASK_PACKET.json",
        "public_launch/qira5/QIRA5_PACKET_GENERATION_RESULT.json",
        "public_launch/qira5/QIRA5_REVIEW_RESULT.json",
        "public_launch/qira5/QIRA5_NEXT_STEPS.md",
        "public_launch/qira5/QIRA_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert Path(path).exists(), path


def test_qira5_docs_preserve_no_execution_boundary():
    text = Path("docs/qira5_pr_packet_generator.md").read_text(encoding="utf-8")

    assert "does not call GitHub APIs" in text
    assert "does not execute" in text
    assert "not verification" in text
