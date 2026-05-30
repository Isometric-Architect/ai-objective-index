from ai_objective_index.portfolio.pilot_discovery_personas import build_discovery_personas, write_personas


def test_personas_generated():
    personas = build_discovery_personas()
    assert len(personas) >= 7
    assert {item["suggested_vertical"] for item in personas} >= {"agentsec", "qira", "datacapsule", "portfolio"}
    assert all(item["manual_only"] is True for item in personas)


def test_personas_write_payload():
    payload = write_personas()
    assert payload["persona_count"] >= 7
    assert payload["auto_contact_performed"] is False
    assert payload["external_api_used"] is False
