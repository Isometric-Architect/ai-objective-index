from ai_objective_index.agent_adoption.discover_mode import discover_capabilities, sample_discover_request


def test_discover_mode_returns_top_candidates_even_if_hold():
    response = discover_capabilities(sample_discover_request())

    assert response["mode"] == "discover"
    assert response["route_decision"] == "HOLD_WITH_ACTIONABLE_NEXT_STEPS"
    assert len(response["top_candidates"]) == 3
    assert response["best_current_candidate"]["preliminary_route_decision"].startswith("HOLD")


def test_discover_mode_candidates_include_next_action_and_must_not_claim():
    response = discover_capabilities()

    for candidate in response["top_candidates"]:
        assert candidate["next_action"]
        assert candidate["must_not_claim"]
        assert candidate["source_trace_refs"]
        assert candidate["residualops_escalation"]


def test_discover_mode_is_public_demo_ranking_without_private_kernel():
    response = discover_capabilities()

    assert response["ranking_method"] == "transparent_public_demo_relevance_fields_only"
    assert response["private_kernel_exposed"] is False
    assert response["external_action_performed"] is False
    assert response["live_network_used"] is False

