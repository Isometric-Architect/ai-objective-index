from ai_objective_index.agent_discovery_eval.ordinary_agent_failure_fixtures import ordinary_agent_eval_cases
from ai_objective_index.agent_discovery_eval.ordinary_agent_prompt_eval import (
    naive_result_for_case,
    run_ordinary_agent_prompt_eval,
)


def test_ordinary_agent_eval_cases_exist():
    cases = ordinary_agent_eval_cases()

    assert len(cases) >= 10
    assert any(case["case_id"] == "tool_available_equals_tool_authorized" for case in cases)


def test_naive_baseline_contains_expected_failure_modes():
    case = ordinary_agent_eval_cases()[0]
    naive = naive_result_for_case(case)

    assert naive["hallucinated_candidate_accepted"] is True
    assert naive["tool_available_is_tool_authorized"] is True


def test_prompt_eval_guided_outscores_naive():
    report = run_ordinary_agent_prompt_eval(write_result=False)

    assert report["aoi_guided_total_score"] > report["naive_total_score"]
    assert "missing HOLD" in report["reduced_failure_modes"]
