from __future__ import annotations

from fastapi.testclient import TestClient

from ai_objective_index.api import app


client = TestClient(app)


def test_status_includes_curated_counts() -> None:
    response = client.get("/status")

    assert response.status_code == 200
    payload = response.json()
    assert "curated_object_count" in payload
    assert "public_beta_object_count" in payload
    assert payload["default_data_scope"] == "sample"


def test_search_curated_scope_works() -> None:
    response = client.get("/search", params={"query": "api", "data_scope": "curated"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_scope"] == "curated"
    assert payload["read_only"] is True


def test_search_public_beta_scope_warns_or_returns_results() -> None:
    response = client.get("/search", params={"query": "api", "data_scope": "public_beta"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["data_scope"] == "public_beta"
    assert payload["read_only"] is True
    assert payload["results"] or payload["warnings"]
