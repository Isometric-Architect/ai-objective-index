from ai_objective_index.agent_discovery_eval.manual_cross_model_intake import run_manual_cross_model_intake


def test_manual_cross_model_intake_generates_three_redacted_packets():
    packets = run_manual_cross_model_intake(write_result=True)

    assert len(packets) == 3
    assert {packet["model_name"] for packet in packets} == {
        "Gemini",
        "GPT-5.5 Thinking",
        "Claude Opus 4.8 High",
    }
    assert all(packet["redaction_status"] == "PASS_REDACTED" for packet in packets)
    assert all(packet["external_llm_api_called"] is False for packet in packets)
    assert all(packet["private_kernel_exposed"] is False for packet in packets)


def test_manual_cross_model_intake_preserves_model_specific_feedback():
    packets = {packet["model_name"]: packet for packet in run_manual_cross_model_intake(write_result=False)}

    assert "adaptive governance" in " ".join(packets["Gemini"]["recommended_killer_features"]).lower()
    assert "Capability Decision Packet" in packets["GPT-5.5 Thinking"]["recommended_killer_features"]
    assert "rug-pull diff" in packets["Claude Opus 4.8 High"]["recommended_killer_features"]
