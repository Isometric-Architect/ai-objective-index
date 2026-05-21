from fastapi.testclient import TestClient

from ai_objective_index.api import app
from ai_objective_index.vnext import execution_receipt_api
from ai_objective_index.vnext.execution_receipt_store import ExecutionReceiptStore


client = TestClient(app)


def test_receipt_status_endpoint_reports_no_execution():
    response = client.get("/v1/execution-receipts/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is True
    assert payload["external_execution"] is False
    assert payload["probe_execution"] is False


def test_submit_and_read_receipt_endpoint(monkeypatch, tmp_path):
    store = ExecutionReceiptStore(tmp_path / "receipts.jsonl", tmp_path / "index.json")
    monkeypatch.setattr(execution_receipt_api, "_store", lambda: store)
    response = client.post(
        "/v1/execution-receipts",
        json={"capability_id": "capability:test", "outcome": "hold", "receipt_origin": "local_fixture"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["stored"] is True
    receipt_id = payload["receipt_id"]

    read_response = client.get(f"/v1/execution-receipts/{receipt_id}")
    assert read_response.status_code == 200
    assert read_response.json()["receipt"]["capability_id"] == "capability:test"


def test_route_with_receipts_endpoint(monkeypatch, tmp_path):
    store = ExecutionReceiptStore(tmp_path / "receipts.jsonl", tmp_path / "index.json")
    monkeypatch.setattr(execution_receipt_api, "_store", lambda: store)
    response = client.post(
        "/v1/objectives/route-with-receipts",
        json={
            "query": "image API",
            "objective": "select source-traced API candidates",
            "domain": "ai_apis",
            "data_scope": "sample",
            "limit": 1,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "receipt_route_overlay" in payload
    assert payload["receipt_route_overlay"]["probe_execution"] is False
