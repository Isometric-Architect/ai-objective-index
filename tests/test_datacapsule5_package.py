from ai_objective_index.datacapsule.package5 import run_datacapsule5_package


def test_datacapsule5_package_result_passes():
    result = run_datacapsule5_package()

    assert result["decision"] == "PASS_DATACAPSULE5_FIXTURE_CORPUS_AND_NEGATIVE_CONTROLS"
    assert result["fixture_count"] >= 8
    assert result["false_pass_count"] == 0
    assert result["can_certify_rights"] is False
    assert result["can_certify_privacy"] is False
    assert result["can_authorize_action"] is False
