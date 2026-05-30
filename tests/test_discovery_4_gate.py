from ai_objective_index.agent_discovery_eval import discovery_4_gate
from ai_objective_index.agent_discovery_eval.discovery_4_gate import run_discovery_4_gate


def test_discovery_4_gate_classifies_full_suite_residual_hold():
    result = run_discovery_4_gate(write_result=True)

    assert result["decision"] == "HOLD_FULL_SUITE_RESIDUAL_CLASSIFIED"
    assert result["feedback_packet_count"] == 3
    assert result["full_suite_green_claim_allowed"] is False


def test_discovery_4_gate_blocks_overclaim(monkeypatch):
    monkeypatch.setattr(discovery_4_gate, "_artifact_text", lambda: "this is security certified")

    result = run_discovery_4_gate(write_result=False, ensure_artifacts=False)

    assert result["decision"] == "BLOCK_FALSE_FULL_SUITE_CLAIM" or result["decision"] == "BLOCK_OVERCLAIM"


def test_discovery_4_gate_blocks_private_kernel_exposure(monkeypatch):
    monkeypatch.setattr(discovery_4_gate, "_artifact_text", lambda: "ranking_weights: 0.42")

    result = run_discovery_4_gate(write_result=False, ensure_artifacts=False)

    assert result["decision"] == "BLOCK_PRIVATE_KERNEL_EXPOSURE"
