from ai_objective_index.portfolio import roe14_feedback_second_run_gate as gate_module
from ai_objective_index.portfolio.pilot_feedback_form import package_pilot_feedback
from ai_objective_index.portfolio.roe14_feedback_second_run_gate import run_roe14_gate


def test_roe14_gate_pass_on_safe_sample():
    result = run_roe14_gate(write_result=True, ensure_samples=True)
    assert result["decision"] == "PASS_PILOT_FEEDBACK_SECOND_RUN_READY"
    assert result["second_run_executed"] is False


def test_roe14_gate_blocks_external_action_fixture(monkeypatch):
    safe = package_pilot_feedback(sample=True)
    unsafe = dict(safe)
    unsafe["second_run_plans"] = [dict(safe["second_run_plans"][0], allowed_operations=["github_api"])]
    monkeypatch.setattr(gate_module, "package_pilot_feedback", lambda sample=True: unsafe)
    result = gate_module.run_roe14_gate(write_result=False, ensure_samples=True)
    assert result["decision"] == "BLOCK_EXTERNAL_ACTION"


def test_roe14_gate_blocks_overclaim_fixture(monkeypatch):
    safe = package_pilot_feedback(sample=True)
    monkeypatch.setattr(gate_module, "scan_feedback_claims", lambda paths: [{"path": "fixture", "line": 1}])
    monkeypatch.setattr(gate_module, "package_pilot_feedback", lambda sample=True: safe)
    result = gate_module.run_roe14_gate(write_result=False, ensure_samples=True)
    assert result["decision"] == "BLOCK_OVERCLAIM"
