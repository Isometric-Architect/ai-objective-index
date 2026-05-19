from ai_objective_index.ai_reviewer_simulation import REVIEWER_ROLES, run_ai_reviewer_simulation


def test_ai_reviewer_simulation_includes_all_roles():
    result = run_ai_reviewer_simulation(write_result=False)

    assert result["overall_token"] in {"PASS", "HOLD", "BLOCK"}
    assert result["external_llm_used"] is False
    assert set(result["reviewers"]) == set(REVIEWER_ROLES)
    for role in REVIEWER_ROLES:
        assert result["reviewers"][role]["token"] in {"PASS", "HOLD", "BLOCK"}
        assert "evidence_files_checked" in result["reviewers"][role]
