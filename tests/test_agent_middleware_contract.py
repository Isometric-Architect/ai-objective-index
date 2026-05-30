from ai_objective_index.agent_adoption.middleware_contract import middleware_contract


def test_agent_middleware_contract_distinguishes_modes_and_boundaries():
    contract = middleware_contract()

    assert set(contract["modes"]) == {"advisory", "enforced", "non_bypassable_proxy"}
    assert "faster candidate discovery" in contract["agent_facing_value"]
    assert "audit trace" in contract["operator_facing_value"]
    assert contract["external_action_authorization"] is False
    assert contract["security_certification"] is False
    assert contract["product_readiness_claim"] is False
