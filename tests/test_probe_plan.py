from ai_objective_index.vnext.probe_card import ProbeCard, ProbePlan


def test_probe_plan_serializes_forbidden_execution():
    plan = ProbePlan(probe_cards=[ProbeCard(capability_id="capability:test")])
    payload = plan.model_dump(mode="json", by_alias=True)
    assert payload["schema"] == "AOI_ProbePlan/v0.1"
    assert "network" in payload["forbidden_execution"]
    assert "deterministic_local_only" in payload["allowed_execution"]
    assert payload["capability_ids"] == ["capability:test"]
