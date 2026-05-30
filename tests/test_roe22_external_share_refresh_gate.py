from ai_objective_index.portfolio import roe22_external_share_refresh_gate as gate_module
from ai_objective_index.portfolio.external_share_refresh_builder import generate_external_share_refresh
from ai_objective_index.portfolio.roe22_external_share_refresh_gate import run_roe22_gate


def test_roe22_gate_passes_current_v2_share_pack():
    result = run_roe22_gate(write_result=True, ensure_share_refresh=True)
    assert result["decision"] == "PASS_EXTERNAL_SHARE_PACK_REFRESHED_FROM_UPDATED_DASHBOARD"
    assert result["agentsec_executed_incorporated_visible"] is True
    assert result["skipped_candidates_visible"] is True


def test_roe22_gate_blocks_network_dependency(monkeypatch):
    safe = generate_external_share_refresh(write_result=True)
    monkeypatch.setattr(gate_module, "generate_external_share_refresh", lambda write_result=True: safe)
    monkeypatch.setattr(gate_module, "html_has_network_dependency", lambda: True)
    result = gate_module.run_roe22_gate(write_result=False, ensure_share_refresh=True)
    assert result["decision"] == "BLOCK_NETWORK_DEPENDENCY"


def test_roe22_gate_blocks_private_kernel_fixture(monkeypatch):
    unsafe = generate_external_share_refresh(write_result=True)
    unsafe = dict(unsafe)
    unsafe["redaction"] = {"decision": "BLOCK_SENSITIVE_CONTENT", "finding_count": 1, "token_printed": False, "private_kernel_exposed": True}
    monkeypatch.setattr(gate_module, "generate_external_share_refresh", lambda write_result=True: unsafe)
    result = gate_module.run_roe22_gate(write_result=False, ensure_share_refresh=True)
    assert result["decision"] == "BLOCK_SECRET_FINDING"


def test_roe22_gate_blocks_skipped_candidate_false_success(monkeypatch):
    safe = generate_external_share_refresh(write_result=True)
    unsafe_cards = {
        "cards": [
            {"vertical": "agentsec", "feedback_second_run_status": "executed", "memory_status": "incorporated"},
            {"vertical": "qira", "feedback_second_run_status": "executed", "memory_status": "incorporated"},
            {"vertical": "datacapsule", "feedback_second_run_status": "skipped_missing_artifact", "memory_status": "skipped_missing_artifact"},
            {"vertical": "portfolio", "feedback_second_run_status": "skipped_missing_artifact", "memory_status": "skipped_missing_artifact"},
        ]
    }
    monkeypatch.setattr(gate_module, "generate_external_share_refresh", lambda write_result=True: safe)
    monkeypatch.setattr(gate_module, "_read_json", lambda path: unsafe_cards if str(path).endswith("STATUS_CARDS_V2.json") else {})
    result = gate_module.run_roe22_gate(write_result=False, ensure_share_refresh=True)
    assert result["decision"] == "BLOCK_SKIPPED_CANDIDATE_FALSE_SUCCESS"
