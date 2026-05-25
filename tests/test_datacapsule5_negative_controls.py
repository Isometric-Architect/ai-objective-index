from ai_objective_index.datacapsule.negative_controls import (
    run_datacapsule5_negative_controls,
    write_negative_control_result,
)


def test_datacapsule5_negative_controls_pass_public_fixtures():
    result = run_datacapsule5_negative_controls()

    assert result["decision"] == "PASS_DATACAPSULE5_NEGATIVE_CONTROLS"
    assert result["false_pass_count"] == 0
    assert result["mismatch_count"] == 0
    assert result["network_used"] is False
    assert result["crawler_used"] is False
    assert result["can_authorize_action"] is False


def test_datacapsule5_negative_controls_catch_false_pass_fixture():
    result = run_datacapsule5_negative_controls(
        [
            {
                "fixture_id": "bad-expectation",
                "primary_use": "retrieve",
                "expected_decision": "BLOCK_UNSUPPORTED_CLAIM",
                "risk_theme": "test_false_pass",
                "payload": {
                    "data_id": "fixture.local/safe-retrieval",
                    "name": "Safe retrieval fixture",
                    "source": "repository-local-fixture",
                    "source_records": ["fixtures/safe.json"],
                    "license": "MIT",
                    "allowed_use": {"retrieve": True},
                },
            }
        ]
    )

    assert result["decision"] == "BLOCK_DATACAPSULE5_NEGATIVE_CONTROL_FALSE_PASS"
    assert result["false_pass_count"] == 1


def test_datacapsule5_negative_controls_writes_outputs():
    result = write_negative_control_result()

    assert result["decision"] == "PASS_DATACAPSULE5_NEGATIVE_CONTROLS"
