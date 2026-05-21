from ai_objective_index.vnext.probe_card import ProbeCard


def test_probe_card_serializes_local_sandbox():
    card = ProbeCard(probe_type="source_trace_integrity", capability_id="capability:test")
    payload = card.model_dump(mode="json", by_alias=True)
    assert payload["schema"] == "AOI_ProbeCard/v0.1"
    assert payload["sandbox_policy"]["no_network"] is True
    assert payload["sandbox_policy"]["no_subprocess"] is True
    assert "quality guaranteed" in payload["forbidden_claims"]
