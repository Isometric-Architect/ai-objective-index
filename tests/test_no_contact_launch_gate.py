from ai_objective_index import no_contact_launch_gate as gate


def test_no_contact_launch_gate_does_not_require_private_reviewer():
    result = gate.run_no_contact_launch_gate(write_result=False)

    assert result["overall_token"] in {"PASS", "HOLD", "BLOCK"}
    assert result["private_reviewer_required"] is False
    assert result["launch_mode"] == "no_contact_public_beta"
    assert result["public_switch_performed"] is False
    assert result["community_post_performed"] is False


def test_no_contact_launch_gate_public_beta_missing_holds(monkeypatch):
    monkeypatch.setattr(gate, "_public_beta_mcp_count", lambda: 0)
    result = gate.run_no_contact_launch_gate(write_result=False)

    assert result["checks"]["public_beta_mcp"]["token"] == "HOLD"
    assert result["overall_token"] in {"HOLD", "BLOCK"}
