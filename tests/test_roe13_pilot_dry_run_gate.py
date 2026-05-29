from ai_objective_index.portfolio import roe13_pilot_dry_run_gate as gate
from ai_objective_index.portfolio.pilot_dry_run import run_pilot_dry_run


def test_roe13_gate_passes_safe_dry_run():
    run_pilot_dry_run(sample=True, write_result=True)
    result = gate.run_roe13_gate(write_result=True)
    assert result["decision"] == "PASS_FIRST_OWNER_CONSENTED_PILOT_DRY_RUN_READY"
    assert result["vertical_count"] == 3
    assert result["redaction_decision"] == "PASS_REDACTED"


def test_roe13_gate_blocks_external_action_fixture(monkeypatch):
    generated = run_pilot_dry_run(sample=True, write_result=True)
    generated["trace"]["github_api_used"] = True
    monkeypatch.setattr(gate, "run_pilot_dry_run", lambda sample=True, write_result=True: generated)
    result = gate.run_roe13_gate(write_result=False, ensure_dry_run=True)
    assert result["decision"] == "BLOCK_EXTERNAL_ACTION"


def test_roe13_gate_blocks_overclaim_fixture(tmp_path):
    fixture = tmp_path / "overclaim.md"
    fixture.write_text("This dry-run provides security certification.", encoding="utf-8")
    findings = gate.scan_dry_run_claims([fixture])
    assert findings
