from ai_objective_index.portfolio.pilot_outreach_operator_checklist import build_do_not_send_guard, build_operator_checklist, write_operator_artifacts


def test_operator_checklist_says_do_not_auto_send():
    checklist = build_operator_checklist()
    guard = build_do_not_send_guard()
    assert "Do not auto-send" in checklist
    assert "does not send anything" in guard
    assert "No API calls" in guard


def test_operator_artifacts_written():
    payload = write_operator_artifacts()
    assert "do_not_send_guard" in payload
    assert "claim_boundary" in payload
