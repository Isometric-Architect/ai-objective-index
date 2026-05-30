from ai_objective_index.portfolio import roe20_feedback_second_run_bridge_gate as gate_module
from ai_objective_index.portfolio.feedback_second_run_executor import run_feedback_second_run_bridge
from ai_objective_index.portfolio.roe20_feedback_second_run_bridge_gate import run_roe20_gate


def test_roe20_gate_passes_on_safe_sample():
    result = run_roe20_gate(write_result=True, ensure_bridge=True)
    assert result["decision"] == "PASS_FEEDBACK_TO_SECOND_RUN_BRIDGE_READY"
    assert result["selected_count"] == 1
    assert result["skipped_count"] == 3


def test_roe20_gate_holds_when_no_ready_candidates(monkeypatch):
    safe = run_feedback_second_run_bridge(sample=True, write_result=True)
    receipt = dict(safe["receipt"])
    receipt["aggregate_summary"] = dict(receipt["aggregate_summary"], selected_count=0, executed_count=0)
    unsafe = dict(safe, receipt=receipt)
    monkeypatch.setattr(gate_module, "run_feedback_second_run_bridge", lambda sample=True, write_result=True: unsafe)
    assert gate_module.run_roe20_gate(write_result=False, ensure_bridge=True)["decision"] == "HOLD_NO_READY_CANDIDATES"


def test_roe20_gate_blocks_external_action_fixture(monkeypatch):
    safe = run_feedback_second_run_bridge(sample=True, write_result=True)
    receipt = dict(safe["receipt"])
    receipt["aggregate_summary"] = dict(receipt["aggregate_summary"], external_action_count=1)
    unsafe = dict(safe, receipt=receipt)
    monkeypatch.setattr(gate_module, "run_feedback_second_run_bridge", lambda sample=True, write_result=True: unsafe)
    assert gate_module.run_roe20_gate(write_result=False, ensure_bridge=True)["decision"] == "BLOCK_EXTERNAL_ACTION"


def test_roe20_gate_blocks_overclaim_fixture(monkeypatch):
    safe = run_feedback_second_run_bridge(sample=True, write_result=True)
    monkeypatch.setattr(gate_module, "scan_feedback_second_run_claims", lambda paths: [{"path": "fixture", "line": 1}])
    monkeypatch.setattr(gate_module, "run_feedback_second_run_bridge", lambda sample=True, write_result=True: safe)
    assert gate_module.run_roe20_gate(write_result=False, ensure_bridge=True)["decision"] == "BLOCK_OVERCLAIM"
