from ai_objective_index.portfolio.agentsec_pilot_feedback_memory import build_feedback_memory_entry


def test_agentsec_pilot_feedback_memory_entry_validates():
    receipt = {
        "pilot_id": "agentsec-pilot-test",
        "decision_summary": {"hold_count": 1, "block_count": 1},
        "findings": [{"category": "permission_scope"}, {"category": "forbidden_action"}],
    }

    entry = build_feedback_memory_entry(receipt).model_dump(mode="json", by_alias=True)

    assert entry["schema"] == "ResidualOps_AgentSecPilotFeedbackMemory/v0.1"
    assert entry["feedback_status"] == "pending"
    assert entry["should_update_policy_profile"] is True
    assert entry["should_add_negative_control"] is True
    assert entry["external_posting_performed"] is False
