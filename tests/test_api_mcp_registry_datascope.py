from __future__ import annotations

from fastapi.testclient import TestClient

from ai_objective_index.api import app
from ai_objective_index.registry_intake.mcp_registry_export import export_mcp_registry_intake


client = TestClient(app)


def test_api_status_includes_mcp_registry_counts() -> None:
    export_mcp_registry_intake(use_fixture=True, allow_network=False)

    response = client.get("/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["default_data_scope"] == "sample"
    assert payload["read_only"] is True
    assert payload["live_network_enabled"] is False
    assert payload["mcp_registry_object_count"] >= 5
    assert "public_beta_mcp_object_count" in payload


def test_api_search_mcp_registry_scope_works() -> None:
    export_mcp_registry_intake(use_fixture=True, allow_network=False)

    response = client.get("/search", params={"query": "browser automation MCP", "data_scope": "mcp_registry"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_scope"] == "mcp_registry"
    assert payload["results"]


def test_api_search_public_beta_mcp_warns_or_returns_results() -> None:
    export_mcp_registry_intake(use_fixture=True, allow_network=False)

    response = client.get("/search", params={"query": "browser automation MCP", "data_scope": "public_beta_mcp"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_scope"] == "public_beta_mcp"
    assert payload["results"] or payload["warnings"]
