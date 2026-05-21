from ai_objective_index import mcp_tools
from ai_objective_index.vnext import execution_receipt_mcp_tools
from ai_objective_index.vnext.execution_receipt_store import ExecutionReceiptStore


def test_mcp_submit_receipt_and_memory(monkeypatch, tmp_path):
    store = ExecutionReceiptStore(tmp_path / "receipts.jsonl", tmp_path / "index.json")
    monkeypatch.setattr(execution_receipt_mcp_tools, "_store", lambda: store)
    result = mcp_tools.submit_execution_receipt(
        {
            "capability_id": "capability:test",
            "outcome": "hold",
            "receipt_origin": "local_fixture",
            "outcome_summary": "Local route remained held.",
        }
    )
    assert result["stored"] is True
    assert result["external_execution"] is False

    memory = mcp_tools.get_capability_receipt_memory("capability:test")
    assert memory["receipt_count"] == 1
    assert memory["verification_guarantee"] is False


def test_mcp_route_with_receipts_offline(monkeypatch, tmp_path):
    store = ExecutionReceiptStore(tmp_path / "receipts.jsonl", tmp_path / "index.json")
    monkeypatch.setattr(execution_receipt_mcp_tools, "_store", lambda: store)
    result = mcp_tools.route_objective_with_receipts(
        query="image API",
        objective="select source-traced API candidates",
        domain="ai_apis",
        data_scope="sample",
        limit=1,
    )
    assert result["read_only"] is True
    assert result["external_execution"] is False
    assert result["probe_execution"] is False
    assert "receipt_route_overlay" in result
