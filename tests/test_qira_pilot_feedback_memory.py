from ai_objective_index.portfolio.qira_pilot_feedback_memory import build_feedback_memory_entry
from ai_objective_index.portfolio.qira_pilot_packager import build_qira_pilot_receipt
from ai_objective_index.portfolio.qira_pilot_receipt import to_jsonable


def test_qira_feedback_memory_entry_validates():
    entry = build_feedback_memory_entry(to_jsonable(build_qira_pilot_receipt(sample=True)))

    assert entry.feedback_status == "pending"
    assert entry.should_add_negative_control is True
    assert entry.should_request_ci_evidence is True
    assert entry.github_api_used is False
