from ai_objective_index.portfolio import roe18_outreach_gate as gate_module
from ai_objective_index.portfolio.pilot_outreach_drafts import generate_outreach_pack
from ai_objective_index.portfolio.roe18_outreach_gate import run_roe18_gate


def test_roe18_gate_passes_generated_pack():
    result = run_roe18_gate(write_result=True, ensure_pack=True)
    assert result["decision"] == "PASS_MANUAL_OUTREACH_DRAFTS_READY"


def test_roe18_gate_blocks_auto_send(monkeypatch):
    safe = generate_outreach_pack(write_result=True)
    unsafe = dict(safe)
    unsafe["auto_send_performed"] = True
    monkeypatch.setattr(gate_module, "generate_outreach_pack", lambda write_result=True: unsafe)
    result = gate_module.run_roe18_gate(write_result=False, ensure_pack=True)
    assert result["decision"] == "BLOCK_AUTO_SEND"


def test_roe18_gate_blocks_external_api(monkeypatch):
    safe = generate_outreach_pack(write_result=True)
    unsafe = dict(safe)
    unsafe["external_api_used"] = True
    monkeypatch.setattr(gate_module, "generate_outreach_pack", lambda write_result=True: unsafe)
    result = gate_module.run_roe18_gate(write_result=False, ensure_pack=True)
    assert result["decision"] == "BLOCK_EXTERNAL_API"


def test_roe18_gate_blocks_overclaim(monkeypatch):
    safe = generate_outreach_pack(write_result=True)
    unsafe = dict(safe)
    unsafe["claim_audit"] = {"decision": "BLOCK_OVERCLAIM", "risky_phrase_count": 1}
    monkeypatch.setattr(gate_module, "generate_outreach_pack", lambda write_result=True: unsafe)
    result = gate_module.run_roe18_gate(write_result=False, ensure_pack=True)
    assert result["decision"] == "BLOCK_OVERCLAIM"
