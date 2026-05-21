from fastapi.testclient import TestClient

from ai_objective_index.api import app
from ai_objective_index.vnext import probe_api
from ai_objective_index.vnext.probe_receipt_store import ProbeReceiptStore


client = TestClient(app)


def test_probe_status_endpoint_reports_local_only():
    response = client.get("/v1/probes/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["local_probe_only"] is True
    assert payload["network"] is False


def test_probe_plan_and_run_endpoints(monkeypatch, tmp_path):
    store = ProbeReceiptStore(tmp_path / "probes.jsonl", tmp_path / "probe_index.json")
    monkeypatch.setattr(probe_api, "_store", lambda: store)
    plan_response = client.post(
        "/v1/probes/plan",
        json={"query": "image API", "objective": "select candidates", "data_scope": "sample", "limit": 1},
    )
    assert plan_response.status_code == 200
    plan = plan_response.json()["probe_plan"]
    run_response = client.post("/v1/probes/run-local", json=plan)
    assert run_response.status_code == 200
    payload = run_response.json()
    assert payload["local_probe_only"] is True
    assert payload["network_used"] is False


def test_route_with_probes_endpoint():
    response = client.post(
        "/v1/objectives/route-with-probes",
        json={"query": "image API", "objective": "select candidates", "data_scope": "sample", "limit": 1},
    )
    assert response.status_code == 200
    assert "probe_route_overlay" in response.json()
