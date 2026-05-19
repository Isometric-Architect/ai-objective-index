from ai_objective_index.post_public_stabilization import run_post_public_stabilization


def test_post_public_stabilization_output_structure():
    result = run_post_public_stabilization(write_result=False)

    assert result["overall_token"] in {"PASS", "HOLD", "BLOCK"}
    assert result["community_post_performed"] is False
    assert result["github_release_created"] is False
    assert result["mcp_registry_submission_performed"] is False
    assert result["checks"]["no_secrets_audit"]["token"] in {"PASS", "HOLD", "BLOCK"}

