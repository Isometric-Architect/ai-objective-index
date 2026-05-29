from ai_objective_index.portfolio.second_run_delta import build_delta_from_result
from ai_objective_index.portfolio.second_run_executor import run_second_run


def test_second_run_deltas_created_for_all_verticals():
    result = run_second_run(sample=True, write_result=True)
    assert {delta["vertical"] for delta in result["deltas"]} == {"agentsec", "qira", "datacapsule"}
    assert all(delta["unsafe_decision_upgrade_detected"] is False for delta in result["deltas"])


def test_second_run_delta_detects_unsafe_upgrade():
    result = {
        "vertical": "agentsec",
        "prior_receipt_ref": "prior",
        "new_receipt_ref": "new",
        "feedback_id": "feedback",
        "prior_decision_summary": {"allow_count": 0, "hold_count": 1, "block_count": 1},
        "new_decision_summary": {"allow_count": 2, "hold_count": 0, "block_count": 0},
    }
    delta = build_delta_from_result(result)
    delta.decision_changes["hold_to_allow_count"] = 1
    delta.unsafe_decision_upgrade_detected = True
    assert delta.unsafe_decision_upgrade_detected is True
