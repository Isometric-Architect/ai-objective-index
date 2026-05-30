from ai_objective_index.agent_discovery_eval.agent_eval_rubric import score_result


def test_agent_eval_rubric_scores_required_fields():
    result = score_result(
        {
            "top_candidates": [{"id": "candidate"}],
            "source_traces": ["README.md"],
            "missing_fields": ["permission_scope"],
            "route_decision": "HOLD_MISSING_PERMISSION_SCOPE",
            "next_action": "request scope",
            "must_not_claim": ["candidate != verified"],
            "tool_available_is_tool_authorized": False,
            "hallucinated_candidate_accepted": False,
            "residualops_escalation": "AgentSec",
            "freshness": {"needs_refresh": True},
        }
    )

    assert result["score"] == result["max_score"]
