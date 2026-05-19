from ai_objective_index.post_public_state_report import run_post_public_state_report


def test_post_public_state_report_links_and_next_options():
    result = run_post_public_state_report(write_result=False)

    assert "github.com/Isometric-Architect/ai-objective-index" in result["github_url"]
    assert "huggingface.co/spaces/edict-lab/ai-objective-index-demo" in result["hf_space_url"]
    assert "huggingface.co/datasets/edict-lab/ai-objective-index-sample" in result["hf_dataset_url"]
    assert result["community_post_performed"] is False
    assert result["github_release_created"] is False
    assert result["mcp_registry_submission_performed"] is False
    assert set(result["next_options"]) == {"A", "B", "C", "D"}
