from pathlib import Path


def test_qira8_docs_exist():
    for path in [
        "docs/qira8_pr_artifact_bundle.md",
        "docs/qira_reviewer_report_limitations.md",
    ]:
        assert Path(path).exists(), path


def test_qira8_outputs_exist():
    for path in [
        "public_launch/qira8/QIRA8_REVIEWER_REPORT.md",
        "public_launch/qira8/QIRA8_PR_COMMENT_DRAFT.md",
        "public_launch/qira8/QIRA8_ARTIFACT_MANIFEST.json",
        "public_launch/qira8/QIRA8_BUNDLE_RESULT.json",
        "public_launch/qira8/QIRA8_NEXT_STEPS.md",
        "public_launch/qira8/QIRA_CLAIM_BOUNDARY_AUDIT.json",
    ]:
        assert Path(path).exists(), path


def test_qira8_report_does_not_post_comment():
    text = Path("public_launch/qira8/QIRA8_PR_COMMENT_DRAFT.md").read_text(encoding="utf-8")
    report = Path("public_launch/qira8/QIRA8_REVIEWER_REPORT.md").read_text(encoding="utf-8")

    assert "draft only" in text
    assert "PR comment posted | `False`" in report
