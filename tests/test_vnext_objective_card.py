from ai_objective_index.vnext import ObjectiveCard


def test_vnext_objective_card_serializes_schema_alias():
    card = ObjectiveCard(
        objective_id="obj-python-release-audit",
        task="audit package release readiness",
        domain="software",
        agent_role="coding_agent",
        desired_output="ALLOW/HOLD/BLOCK with evidence",
        forbidden_actions=["upload_pypi", "submit_registry"],
    )

    payload = card.model_dump(by_alias=True)
    assert payload["schema"] == "aoi.vnext.objective_card.v0_3"
    assert "upload_pypi" in payload["forbidden_actions"]
    assert "not verified" in payload["claim_ceiling"]
