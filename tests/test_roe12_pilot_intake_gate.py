from ai_objective_index.portfolio import roe12_pilot_intake_gate as gate
from ai_objective_index.portfolio.pilot_intake_packager import package_pilot_intake


def test_roe12_gate_passes_safe_samples():
    package_pilot_intake(sample=True)
    result = gate.run_roe12_gate(write_result=True)
    assert result["decision"] == "PASS_OWNER_CONSENTED_PILOT_INTAKE_READY"
    assert result["route_ready_count"] == 3
    assert result["redaction_decision"] == "PASS_REDACTED"


def test_roe12_gate_blocks_external_action_fixture(monkeypatch):
    package_pilot_intake(sample=True)
    original_read_json = gate._read_json

    def fake_read_json(path):
        payload = original_read_json(path)
        if str(path).endswith("PILOT_INTAKE_PACKET_SAMPLE_AGENTSEC.json"):
            payload["allowed_review_scope"]["github_api_call"] = True
        return payload

    monkeypatch.setattr(gate, "_read_json", fake_read_json)
    result = gate.run_roe12_gate(write_result=False, ensure_packaged=False)
    assert result["decision"] == "BLOCK_EXTERNAL_ACTION"


def test_roe12_gate_blocks_overclaim_fixture(tmp_path):
    fixture = tmp_path / "overclaim.md"
    fixture.write_text("This intake provides security certification.", encoding="utf-8")
    findings = gate.scan_intake_claims([fixture])
    assert findings
