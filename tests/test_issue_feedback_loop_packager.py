from pathlib import Path

from ai_objective_index.issue_feedback_loop_packager import ISSUE_LABELS, create_issue_feedback_loop_plan


def test_issue_feedback_loop_packager_writes_plan():
    result = create_issue_feedback_loop_plan()
    plan = Path(result["plan_path"])
    text = plan.read_text(encoding="utf-8").lower()

    assert plan.exists()
    for label in ISSUE_LABELS:
        assert label in text
    assert "golden queries" in text
    assert "no direct sales required" in text
    assert result["private_reviewer_required"] is False
