from fastapi.testclient import TestClient

from ai_objective_index.api import app


client = TestClient(app)


def test_rest_objective_route_returns_200():
    response = client.post(
        "/v1/objectives/route",
        json={
            "query": "image API",
            "objective": "select source-traced API candidates",
            "domain": "ai_apis",
            "data_scope": "sample",
            "limit": 2,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["schema"] == "AOI_ObjectiveRouteResponse/v0.1"
    assert payload["read_only"] is True
    assert payload["probe_execution"] is False


def test_rest_router_status_reports_read_only_boundaries():
    response = client.get("/v1/objectives/router/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is True
    assert payload["probe_execution"] is False
    assert "ALLOW_CANDIDATE" in payload["supported_decision_labels"]


def test_rest_capability_trust_not_found_is_stable_404():
    response = client.get("/v1/capabilities/capability:not-real/trust")
    assert response.status_code == 404
    assert response.json()["error"] == "capability_not_found"
