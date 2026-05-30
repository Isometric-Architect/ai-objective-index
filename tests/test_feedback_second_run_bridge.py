from ai_objective_index.portfolio.feedback_second_run_bridge import build_agentsec_feedback_second_run_result


def test_agentsec_feedback_second_run_bridge_result_is_local_only():
    result = build_agentsec_feedback_second_run_result(
        {
            "second_run_candidate_id": "candidate-agentsec",
            "reply_id": "reply-agentsec",
            "vertical": "agentsec",
        }
    )
    assert result["vertical"] == "agentsec"
    assert result["new_decision_summary"] == {"allow_count": 1, "hold_count": 1, "block_count": 1}
    assert result["external_actions_performed"] is False
    assert result["decision_upgrade_performed"] is False
