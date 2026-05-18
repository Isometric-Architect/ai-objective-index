from ai_objective_index.launch_dry_run import run_launch_dry_run, save_launch_dry_run


def test_launch_dry_run_runs_locally():
    result = run_launch_dry_run()
    path = save_launch_dry_run(result)

    assert path.exists()
    assert result["actual_publish_performed"] is False
    assert result["live_network_used"] is False
    assert "checks" in result
