from fastapi.testclient import TestClient

from ai_objective_index.api import app


client = TestClient(app)


def test_status_returns_datascope_counts():
    response = client.get("/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is True
    assert payload["default_data_scope"] == "sample"
    assert payload["live_network_enabled"] is False
    assert payload["productization_mode"] is True
    assert payload["sample_object_count"] > 0
    assert payload["generated_object_count"] >= 3
    assert payload["integrated_object_count"] >= payload["sample_object_count"] + payload["generated_object_count"]


def test_search_default_uses_sample_scope():
    response = client.get("/search", params={"query": "api", "limit": 100})
    assert response.status_code == 200
    payload = response.json()
    assert payload["data_scope"] == "sample"


def test_search_integrated_scope_has_at_least_sample_results_for_broad_query():
    sample = client.get("/search", params={"query": "api", "limit": 100}).json()
    integrated = client.get(
        "/search",
        params={"query": "api", "limit": 100, "data_scope": "integrated"},
    ).json()
    assert integrated["data_scope"] == "integrated"
    assert len(integrated["results"]) >= len(sample["results"])


def test_invalid_datascope_returns_validation_error():
    response = client.get("/search", params={"query": "api", "data_scope": "invalid"})
    assert response.status_code == 422
