from pathlib import Path

from ai_objective_index.portfolio.pilot_feedback_intake_form import FEEDBACK_FORM_PATH, build_feedback_intake_form, write_feedback_intake_form


def test_feedback_form_template_exists_and_sets_boundaries():
    content = build_feedback_intake_form()
    assert "Which artifact did you review?" in content
    assert "Do not include tokens" in content
    assert "not certification" in content
    write_feedback_intake_form()
    assert Path(FEEDBACK_FORM_PATH).exists()
