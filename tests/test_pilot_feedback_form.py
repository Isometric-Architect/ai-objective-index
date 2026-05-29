from ai_objective_index.portfolio.pilot_feedback_form import FORM_TEMPLATE_PATH, package_pilot_feedback
from ai_objective_index.real_pypi_upload_gate import _repo_root


def test_feedback_form_template_exists():
    result = package_pilot_feedback(sample=True)
    assert len(result["feedback_packets"]) == 3
    assert (_repo_root() / FORM_TEMPLATE_PATH).exists()
    assert result["redaction"]["decision"] == "PASS_REDACTED"
