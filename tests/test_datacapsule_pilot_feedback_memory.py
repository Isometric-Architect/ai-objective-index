from ai_objective_index.portfolio.datacapsule_pilot_feedback_memory import build_feedback_memory_entry
from ai_objective_index.portfolio.datacapsule_pilot_packager import build_datacapsule_pilot_receipt
from ai_objective_index.portfolio.datacapsule_pilot_receipt import to_jsonable


def test_datacapsule_feedback_memory_entry_validates():
    entry = build_feedback_memory_entry(to_jsonable(build_datacapsule_pilot_receipt(sample=True)))

    assert entry.feedback_status == "pending"
    assert entry.should_add_negative_control is True
    assert entry.should_request_license_evidence is True
    assert entry.should_request_privacy_evidence is True
    assert entry.should_request_eval_split_evidence is True
