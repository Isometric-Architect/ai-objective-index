from ai_objective_index.portfolio import roe17_external_share_gate as gate_module
from ai_objective_index.portfolio.external_share_pack_builder import generate_external_share_pack
from ai_objective_index.portfolio.roe17_external_share_gate import run_roe17_gate


def test_roe17_gate_passes_current_share_pack():
    result = run_roe17_gate(write_result=True, ensure_share_pack=True)
    assert result["decision"] == "PASS_EXTERNAL_SAFE_DEMO_SHARE_PACK_READY"


def test_roe17_gate_blocks_network_dependency(monkeypatch):
    safe = generate_external_share_pack(write_result=True)
    monkeypatch.setattr(gate_module, "generate_external_share_pack", lambda write_result=True: safe)
    monkeypatch.setattr(gate_module, "html_has_network_dependency", lambda: True)
    result = gate_module.run_roe17_gate(write_result=False, ensure_share_pack=True)
    assert result["decision"] == "BLOCK_NETWORK_DEPENDENCY"


def test_roe17_gate_blocks_private_kernel_fixture(monkeypatch):
    unsafe = generate_external_share_pack(write_result=True)
    unsafe = dict(unsafe)
    unsafe["redaction"] = {"decision": "BLOCK_SENSITIVE_CONTENT", "finding_count": 1, "token_printed": False, "private_kernel_exposed": True}
    monkeypatch.setattr(gate_module, "generate_external_share_pack", lambda write_result=True: unsafe)
    result = gate_module.run_roe17_gate(write_result=False, ensure_share_pack=True)
    assert result["decision"] == "BLOCK_SECRET_FINDING"
