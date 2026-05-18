from __future__ import annotations

from fastapi.testclient import TestClient

from ai_objective_index.api import app
from ai_objective_index.registry_intake.registry_beta_dataset_builder import build_registry_beta_dataset


client = TestClient(app)


def test_api_status_includes_public_beta_mcp_definition() -> None:
    build_registry_beta_dataset()

    response = client.get("/status")
    payload = response.json()

    assert response.status_code == 200
    assert "public_beta_mcp_object_count" in payload
    assert payload["public_beta_mcp_definition"] == "registry_metadata_candidate_not_verified"


def test_api_public_beta_mcp_search_returns_candidates_or_warning() -> None:
    build_registry_beta_dataset()

    response = client.get("/search", params={"query": "browser automation MCP", "data_scope": "public_beta_mcp"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["data_scope"] == "public_beta_mcp"
    assert payload["results"] or payload["warnings"]
    for item in payload["results"]:
        assert item["status"] != "VERIFIED"
        assert item["status"] != "ACTION_READY"
