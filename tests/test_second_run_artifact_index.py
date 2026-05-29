from ai_objective_index.portfolio.second_run_executor import run_second_run


def test_second_run_artifact_index_created():
    result = run_second_run(sample=True, write_result=True)
    assert result["artifact_index"]["artifact_count"] >= 10
    assert all(item["safe_to_share_publicly"] is True for item in result["artifact_index"]["artifacts"])
