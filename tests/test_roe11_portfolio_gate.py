from ai_objective_index.portfolio import roe11_portfolio_gate as gate
from ai_objective_index.portfolio.residualops_unified_readout import generate_unified_portfolio


def test_roe11_gate_passes_current_portfolio():
    generate_unified_portfolio(write_result=True)
    result = gate.run_roe11_gate(write_result=True)
    assert result["decision"] == "PASS_UNIFIED_PILOT_PORTFOLIO_READY"
    assert result["vertical_count"] == 3
    assert result["redaction_decision"] == "PASS_REDACTED"


def test_roe11_gate_blocks_external_action_fixture(monkeypatch):
    generated = generate_unified_portfolio(write_result=True)
    generated["portfolio"]["external_action_used"] = True
    monkeypatch.setattr(gate, "generate_unified_portfolio", lambda write_result=True: generated)
    result = gate.run_roe11_gate(write_result=False, ensure_portfolio=True)
    assert result["decision"] == "BLOCK_EXTERNAL_ACTION"
