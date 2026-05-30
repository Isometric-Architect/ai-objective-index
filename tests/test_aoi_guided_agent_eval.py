from ai_objective_index.agent_discovery_eval.aoi_guided_agent_eval import aoi_guided_result_for_case
from ai_objective_index.agent_discovery_eval.ordinary_agent_failure_fixtures import ordinary_agent_eval_cases


def test_aoi_guided_result_includes_required_fields_and_boundaries():
    result = aoi_guided_result_for_case(ordinary_agent_eval_cases()[0])

    assert result["top_candidates"]
    assert result["source_traces"]
    assert result["missing_fields"]
    assert result["next_action"]
    assert result["must_not_claim"]
    assert result["tool_available_is_tool_authorized"] is False
    assert result["certification_or_readiness_claimed"] is False


def test_all_hold_candidate_set_still_has_next_action():
    case = next(item for item in ordinary_agent_eval_cases() if item["case_id"] == "hold_without_next_action")
    result = aoi_guided_result_for_case(case)

    assert all(candidate["preliminary_route_decision"].startswith("HOLD") for candidate in result["top_candidates"])
    assert result["next_action"]
