from ai_objective_index import public_launch_gate as gate


def test_public_launch_gate_returns_structure():
    result = gate.run_public_launch_gate(write_result=False)

    assert result["overall_token"] in {"PASS", "HOLD", "BLOCK"}
    assert result["public_switch_performed"] is False
    assert result["required_manual_confirmation"] is True


def test_public_launch_gate_public_beta_missing_holds(monkeypatch):
    monkeypatch.setattr(gate, "_public_beta_mcp_count", lambda: 0)
    result = gate.run_public_launch_gate(write_result=False)

    assert result["checks"]["public_beta_mcp"]["token"] == "HOLD"
    assert result["overall_token"] in {"HOLD", "BLOCK"}
