from ai_objective_index.portfolio.pilot_intake_feedback_memory import build_feedback_memory_entry, feedback_memory_to_jsonable


def test_feedback_memory_entry_validates():
    memory = build_feedback_memory_entry(
        {
            "intake_id": "intake-1",
            "route_id": "route-1",
            "selected_vertical": "hold_manual_triage",
            "blockers": ["unknown_artifact"],
        }
    )
    payload = feedback_memory_to_jsonable(memory)
    assert payload["schema"] == "ResidualOps_PilotIntakeFeedbackMemory/v0.1"
    assert payload["feedback_status"] == "pending"
    assert payload["should_change_vertical_route"] is True
