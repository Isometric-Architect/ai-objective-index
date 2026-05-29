from ai_objective_index.portfolio import roe16_dashboard_gate as gate_module
from ai_objective_index.portfolio.pilot_dashboard_builder import generate_dashboard
from ai_objective_index.portfolio.roe16_dashboard_gate import run_roe16_gate


def test_roe16_gate_pass_on_current_artifacts():
    result = run_roe16_gate(write_result=True, ensure_dashboard=True)
    assert result["decision"] == "PASS_PILOT_DASHBOARD_ARTIFACT_READY"


def test_roe16_gate_blocks_external_html_dependency(monkeypatch):
    safe = generate_dashboard(write_result=True)
    monkeypatch.setattr(gate_module, "generate_dashboard", lambda write_result=True: safe)
    monkeypatch.setattr(gate_module, "html_has_external_dependency", lambda: True)
    result = gate_module.run_roe16_gate(write_result=False, ensure_dashboard=True)
    assert result["decision"] == "BLOCK_EXTERNAL_NETWORK_DEPENDENCY"


def test_roe16_gate_blocks_overclaim(monkeypatch):
    safe = generate_dashboard(write_result=True)
    unsafe = dict(safe)
    unsafe["claim_audit"] = {"decision": "BLOCK_OVERCLAIM", "risky_phrase_count": 1}
    monkeypatch.setattr(gate_module, "generate_dashboard", lambda write_result=True: unsafe)
    result = gate_module.run_roe16_gate(write_result=False, ensure_dashboard=True)
    assert result["decision"] == "BLOCK_OVERCLAIM"
