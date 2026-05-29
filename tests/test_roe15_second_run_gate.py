from ai_objective_index.portfolio import roe15_second_run_gate as gate_module
from ai_objective_index.portfolio.roe15_second_run_gate import run_roe15_gate
from ai_objective_index.portfolio.second_run_executor import run_second_run


def test_roe15_gate_pass_on_safe_sample():
    result = run_roe15_gate(write_result=True, ensure_second_run=True)
    assert result["decision"] == "PASS_LOCAL_SECOND_RUN_RECEIPT_READY"
    assert result["unsafe_decision_upgrade_detected"] is False


def test_roe15_gate_blocks_external_action_fixture(monkeypatch):
    safe = run_second_run(sample=True, write_result=True)
    unsafe = dict(safe)
    receipt = dict(safe["receipt"])
    receipt["external_actions_performed"] = True
    unsafe["receipt"] = receipt
    monkeypatch.setattr(gate_module, "run_second_run", lambda sample=True, write_result=True: unsafe)
    result = gate_module.run_roe15_gate(write_result=False, ensure_second_run=True)
    assert result["decision"] == "BLOCK_EXTERNAL_ACTION"


def test_roe15_gate_blocks_unsafe_decision_upgrade_fixture(monkeypatch):
    safe = run_second_run(sample=True, write_result=True)
    unsafe = dict(safe)
    receipt = dict(safe["receipt"])
    deltas = [dict(delta) for delta in receipt["deltas"]]
    deltas[0]["decision_changes"] = dict(deltas[0]["decision_changes"], block_to_allow_count=1)
    receipt["deltas"] = deltas
    unsafe["receipt"] = receipt
    monkeypatch.setattr(gate_module, "run_second_run", lambda sample=True, write_result=True: unsafe)
    result = gate_module.run_roe15_gate(write_result=False, ensure_second_run=True)
    assert result["decision"] == "BLOCK_UNSAFE_DECISION_UPGRADE"


def test_roe15_gate_blocks_overclaim_fixture(monkeypatch):
    safe = run_second_run(sample=True, write_result=True)
    monkeypatch.setattr(gate_module, "scan_second_run_claims", lambda paths: [{"path": "fixture", "line": 1}])
    monkeypatch.setattr(gate_module, "run_second_run", lambda sample=True, write_result=True: safe)
    result = gate_module.run_roe15_gate(write_result=False, ensure_second_run=True)
    assert result["decision"] == "BLOCK_OVERCLAIM"
