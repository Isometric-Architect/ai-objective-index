from ai_objective_index.agent_adoption.agent_output_contract import (
    REQUIRED_OUTPUT_KEYS,
    build_output_contract_examples,
    validate_output_contract,
)


def test_output_contract_has_required_keys():
    payload = build_output_contract_examples()

    assert validate_output_contract(payload) == []
    assert payload["required_output_keys"] == REQUIRED_OUTPUT_KEYS


def test_output_contract_corrects_ordinary_agent_bad_behavior():
    payload = build_output_contract_examples()

    assert "availability with authorization" in payload["ordinary_agent_bad_behavior_example"]["why_bad"]
    corrected = payload["corrected_aoi_behavior_example"]
    assert corrected["route_decision"].startswith("HOLD")
    assert corrected["next_action"]

