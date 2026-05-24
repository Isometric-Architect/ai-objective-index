from ai_objective_index.datacapsule.negative_controls import negative_control_summary, run_datacapsule_negative_controls


def test_datacapsule_negative_controls_have_no_false_passes():
    controls = run_datacapsule_negative_controls()
    summary = negative_control_summary(controls)

    assert summary["control_count"] == 4
    assert summary["false_pass_count"] == 0
    assert all(control.result == "PASS_NEGATIVE_CONTROL" for control in controls)


def test_datacapsule_negative_controls_cover_action_and_prompt_injection():
    controls = {control.control_id: control for control in run_datacapsule_negative_controls()}

    assert controls["action_use_blocks"].actual_decision == "BLOCK_ACTION_USE"
    assert controls["prompt_injection_holds"].actual_decision == "HOLD_PROMPT_INJECTION_REVIEW"
