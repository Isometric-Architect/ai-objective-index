from ai_objective_index.portfolio.roe19_feedback_reply_gate import run_roe19_gate


def test_roe19_gate_passes_on_safe_sample():
    result = run_roe19_gate()
    assert result["decision"] == "PASS_FEEDBACK_REPLY_PACKET_INTAKE_READY"
    assert result["reply_packet_count"] == 4
    assert result["auto_send_performed"] is False


def test_roe19_gate_blocks_external_action_fixture(monkeypatch):
    import ai_objective_index.portfolio.roe19_feedback_reply_gate as gate

    def fake_pack(sample=True):
        return {
            "packets": [{}],
            "classifications": [{"classification": "BLOCK_EXTERNAL_ACTION_REQUEST"}],
            "routes": [{}],
            "triage": [{}],
            "memory_candidates": [{}],
            "second_run_candidates": [{}],
            "redaction": {"decision": "PASS_REDACTED", "finding_count": 0},
        }

    monkeypatch.setattr(gate, "package_feedback_replies", fake_pack)
    assert gate.run_roe19_gate(write_result=False)["decision"] == "BLOCK_EXTERNAL_ACTION"


def test_roe19_gate_blocks_overclaim_fixture(monkeypatch):
    import ai_objective_index.portfolio.roe19_feedback_reply_gate as gate

    def fake_pack(sample=True):
        return {
            "packets": [{}],
            "classifications": [{"classification": "BLOCK_CERTIFICATION_OR_READINESS_CLAIM"}],
            "routes": [{}],
            "triage": [{}],
            "memory_candidates": [{}],
            "second_run_candidates": [{}],
            "redaction": {"decision": "PASS_REDACTED", "finding_count": 0},
        }

    monkeypatch.setattr(gate, "package_feedback_replies", fake_pack)
    assert gate.run_roe19_gate(write_result=False)["decision"] == "BLOCK_OVERCLAIM"
