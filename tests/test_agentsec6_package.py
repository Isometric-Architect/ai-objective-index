from ai_objective_index.agentsec.package6 import run_agentsec6_package


def test_agentsec6_package_result_passes_with_conservative_counts():
    result = run_agentsec6_package()

    assert result["decision"] == "PASS_AGENTSEC6_LOCAL_MANIFEST_CORPUS_PACKAGE"
    assert result["manifest_count"] >= 5
    assert result["allow_count"] >= 1
    assert result["hold_count"] >= 1
    assert result["block_count"] >= 1
    assert result["can_certify_security"] is False
    assert result["can_authorize_action"] is False
