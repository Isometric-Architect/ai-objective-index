from fastapi.testclient import TestClient

from ai_objective_index.api import app


client = TestClient(app)


def test_status_works_and_is_read_only():
    response = client.get("/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "ai-objective-index"
    assert payload["read_only"] is True
    assert payload["object_count"] == 20
    assert "payment" in payload["forbidden_actions"]


def test_search_returns_results():
    response = client.get(
        "/search",
        params={
            "query": "cheap image generation API",
            "objective": "low cost commercial use",
            "limit": 5,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is True
    assert payload["results"]
    assert payload["limitations"]


def test_get_known_object():
    response = client.get("/objects/aoi-pixelforge-api")

    assert response.status_code == 200
    assert response.json()["object_id"] == "aoi-pixelforge-api"


def test_unknown_object_returns_404():
    response = client.get("/objects/aoi-does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": "object_not_found",
        "object_id": "aoi-does-not-exist",
        "message": "No object found for object_id.",
    }


def test_rank_works():
    response = client.post(
        "/rank",
        json={
            "options": [
                {"name": "PixelForge API"},
                {"name": "Unknown Tool", "url": "https://unknown.example.com"},
            ],
            "objective": "cheap image generation API with commercial use terms",
            "constraints": {"budget_max": 50},
            "scoring_profile": "commercial_use",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is True
    assert len(payload["results"]) == 2


def test_compare_works():
    response = client.post(
        "/compare",
        json={
            "object_ids": ["aoi-pixelforge-api", "aoi-motioncanvas-ai"],
            "compare_fields": ["pricing", "docs", "policies", "status"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is True
    assert len(payload["comparison_table"]) == 2


def test_score_works():
    response = client.get("/objects/aoi-pixelforge-api/score")

    assert response.status_code == 200
    payload = response.json()
    assert payload["objective_score"] >= 0
    assert payload["rank_reason"]
    assert payload["penalties"]


def test_source_trace_works():
    response = client.get("/objects/aoi-pixelforge-api/source-trace", params={"field": "pricing"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["traces"]) == 1
    assert payload["traces"][0]["field"] == "pricing"


def test_missing_fields_works():
    response = client.get("/objects/aoi-pixelforge-api/missing-fields")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload["missing_fields"], list)


def test_decision_receipt_works_and_includes_known_limits():
    response = client.post(
        "/decision-receipt",
        json={
            "query": "cheap image generation API with commercial use terms",
            "selected_object_id": "aoi-pixelforge-api",
            "alternatives": ["aoi-motioncanvas-ai"],
            "constraints": {"budget_max": 50},
        },
    )

    assert response.status_code == 200
    receipt = response.json()["decision_receipt"]
    assert "v0.1 read-only benchmark output" in receipt["known_limits"]
    assert "not a quality guarantee" in receipt["known_limits"]


def test_openapi_json_works():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    assert "/search" in payload["paths"]
    assert "/status" in payload["paths"]

