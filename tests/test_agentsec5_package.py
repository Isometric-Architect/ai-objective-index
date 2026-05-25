from ai_objective_index.agentsec.package5 import run_agentsec5_package


def test_agentsec5_package_result_passes():
    result = run_agentsec5_package()

    assert result["decision"] == "PASS_AGENTSEC5_FIXTURE_CORPUS_AND_NEGATIVE_CONTROLS"
    assert result["fixture_count"] >= 6
    assert result["false_pass_count"] == 0
    assert result["can_certify_security"] is False
    assert result["can_authorize_action"] is False
