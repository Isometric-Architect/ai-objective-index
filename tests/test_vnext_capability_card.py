from ai_objective_index.vnext import CapabilityCard


def test_vnext_capability_card_records_boundaries():
    card = CapabilityCard(
        capability_id="cap-twine-check",
        provider="python-packaging",
        name="twine check",
        supported_objectives=["python_package_release_audit"],
        allowed_use=["metadata validation"],
        hold_use=["upload readiness without account"],
        blocked_use=["automatic upload"],
    )

    payload = card.model_dump(by_alias=True)
    assert payload["schema"] == "aoi.vnext.capability_card.v0_3"
    assert payload["name"] == "twine check"
    assert "automatic upload" in payload["blocked_use"]
