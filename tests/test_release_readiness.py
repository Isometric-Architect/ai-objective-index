from ai_objective_index.release_readiness import run_release_readiness, save_release_readiness


def test_release_readiness_helper_runs():
    result = run_release_readiness()

    assert result["overall_token"] in {"PASS", "HOLD", "BLOCK"}
    assert result["read_only"] is True
    assert result["actual_publish_performed"] is False
    assert result["live_network_used"] is False
    assert "checks" in result

    path = save_release_readiness(result)
    assert path.exists()
