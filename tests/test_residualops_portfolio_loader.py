from pathlib import Path

from ai_objective_index.portfolio import residualops_portfolio_loader as loader


def test_loader_handles_all_three_receipts():
    loaded = loader.load_all_pilot_receipts()
    assert loaded["vertical_count"] == 3
    assert {item["vertical_id"] for item in loaded["verticals"]} == {"agentsec", "qira", "datacapsule"}
    assert sum(item["allow_count"] for item in loaded["verticals"]) == 3
    assert sum(item["hold_count"] for item in loaded["verticals"]) == 3
    assert sum(item["block_count"] for item in loaded["verticals"]) == 3
    assert not loaded["external_action_used"]


def test_loader_missing_receipt_produces_hold(tmp_path, monkeypatch):
    monkeypatch.setattr(loader, "_repo_root", lambda: Path(tmp_path))
    result = loader.load_agentsec_receipt()
    assert result["missing_receipt"] is True
    assert result["primary_decision"] == "HOLD_MISSING_RECEIPT"
