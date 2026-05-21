from ai_objective_index.vnext.probe_negative_controls import run_negative_controls


def test_negative_controls_have_zero_false_passes():
    result = run_negative_controls()
    assert result["overall_token"] == "PASS"
    assert result["false_pass_count"] == 0
    assert result["network_used"] is False
