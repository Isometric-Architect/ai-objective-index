from ai_objective_index.agentsec.negative_controls import (
    run_agentsec5_negative_controls,
    write_negative_control_result,
)


def test_agentsec5_negative_controls_pass_public_fixtures():
    result = run_agentsec5_negative_controls()

    assert result["decision"] == "PASS_AGENTSEC5_NEGATIVE_CONTROLS"
    assert result["false_pass_count"] == 0
    assert result["mismatch_count"] == 0
    assert result["network_used"] is False
    assert result["external_tool_executed"] is False


def test_agentsec5_negative_controls_catch_false_pass_fixture():
    result = run_agentsec5_negative_controls(
        [
            {
                "fixture_id": "bad-expectation",
                "expected_decision": "BLOCK_FORBIDDEN_ACTION",
                "risk_theme": "test_false_pass",
                "payload": {
                    "name": "safe-test-fixture",
                    "id": "fixture.local/safe-test-fixture",
                    "description": "Summarizes supplied metadata.",
                },
            }
        ]
    )

    assert result["decision"] == "BLOCK_AGENTSEC5_NEGATIVE_CONTROL_FALSE_PASS"
    assert result["false_pass_count"] == 1


def test_agentsec5_negative_controls_writes_outputs():
    result = write_negative_control_result()

    assert result["decision"] == "PASS_AGENTSEC5_NEGATIVE_CONTROLS"
