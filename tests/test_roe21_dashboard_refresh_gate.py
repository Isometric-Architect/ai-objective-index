from ai_objective_index.portfolio import roe21_dashboard_refresh_gate as gate_module
from ai_objective_index.portfolio.dashboard_refresh_from_feedback import refresh_dashboard_from_feedback
from ai_objective_index.portfolio.roe21_dashboard_refresh_gate import run_roe21_gate


def test_roe21_gate_passes_on_current_artifacts():
    result = run_roe21_gate(write_result=True, ensure_refresh=True)
    assert result["decision"] == "PASS_DASHBOARD_REFRESHED_FROM_FEEDBACK_SECOND_RUN"
    assert result["feedback_bridge_selected_count"] == 1
    assert result["feedback_bridge_skipped_count"] == 3


def test_roe21_gate_blocks_skipped_candidate_false_success(monkeypatch):
    safe = refresh_dashboard_from_feedback(write_result=True)
    unsafe_cards = dict(safe["status_cards"])
    unsafe_cards["cards"] = [dict(card) for card in unsafe_cards["cards"]]
    for card in unsafe_cards["cards"]:
        if card["vertical"] == "qira":
            card["feedback_second_run_status"] = "executed"
            card["memory_status"] = "incorporated"
    unsafe = dict(safe, status_cards=unsafe_cards)
    monkeypatch.setattr(gate_module, "refresh_dashboard_from_feedback", lambda write_result=True: unsafe)
    assert gate_module.run_roe21_gate(write_result=False, ensure_refresh=True)["decision"] == "BLOCK_SKIPPED_CANDIDATE_FALSE_SUCCESS"


def test_roe21_gate_blocks_external_action_fixture(monkeypatch):
    safe = refresh_dashboard_from_feedback(write_result=True)
    delta = dict(safe["delta"])
    delta["aggregate_after"] = dict(delta["aggregate_after"], external_action_count=1)
    unsafe = dict(safe, delta=delta)
    monkeypatch.setattr(gate_module, "refresh_dashboard_from_feedback", lambda write_result=True: unsafe)
    assert gate_module.run_roe21_gate(write_result=False, ensure_refresh=True)["decision"] == "BLOCK_EXTERNAL_ACTION"
