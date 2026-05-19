from ai_objective_index.public_ops_baseline import run_public_ops_baseline


def test_public_ops_baseline_structure():
    result = run_public_ops_baseline(write_result=False)

    assert result["github_url"].startswith("https://github.com/")
    assert result["community_post_performed"] is False
    assert result["github_release_created"] is False
    assert result["mcp_registry_submission_performed"] is False
    assert result["current_recommended_mode"] == "observe_72h"

