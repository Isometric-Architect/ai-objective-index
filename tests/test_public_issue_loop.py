from pathlib import Path

from ai_objective_index.public_issue_loop import run_public_issue_loop


def test_public_issue_loop_creates_templates_and_labels():
    result = run_public_issue_loop(write_result=True)

    assert result["feedback_loop_ready"] is True
    assert Path("public_launch/GITHUB_LABELS_SUGGESTED.md").exists()
    assert Path("public_launch/FIRST_ISSUE_TEMPLATES_CHECK.md").exists()
    assert "failed-query" in result["labels_suggested"]
    assert result["golden_queries"]
    assert Path(".github/ISSUE_TEMPLATE/missing_source_trace.md").exists()
    assert Path(".github/ISSUE_TEMPLATE/install_failure.md").exists()

