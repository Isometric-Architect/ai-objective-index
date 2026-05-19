from ai_objective_index.prepublic_state_report import run_prepublic_state_report


def test_prepublic_state_report_includes_links_and_options():
    result = run_prepublic_state_report(write_result=False)

    assert "github.com/Isometric-Architect/ai-objective-index" in result["github_repo_url"]
    assert "huggingface.co/spaces/edict-lab/ai-objective-index-demo" in result["hf_space_url"]
    assert "huggingface.co/datasets/edict-lab/ai-objective-index-sample" in result["hf_dataset_url"]
    assert set(result["next_options"]) == {"A", "B", "C"}
    assert result["public_switch_performed"] is False
