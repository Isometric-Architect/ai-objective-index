from __future__ import annotations

from ai_objective_index.registry_intake.mcp_registry_client import (
    fetch_registry_servers,
    load_raw_registry_fixture,
)


def test_allow_network_false_does_not_fetch() -> None:
    result = fetch_registry_servers(allow_network=False)

    assert result["live_network_used"] is False
    assert "Live network fetch disabled" in result["error"]
    assert result["servers"] == []


def test_fixture_load_works() -> None:
    fixture = load_raw_registry_fixture()

    assert fixture["fixture_only"] is True
    assert len(fixture["servers"]) >= 5
