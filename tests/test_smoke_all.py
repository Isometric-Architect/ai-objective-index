from pathlib import Path

from ai_objective_index.smoke_all import run_smoke_all


def test_smoke_all_runs_and_writes_result():
    result = run_smoke_all()

    assert result["live_network_used"] is False
    assert result["forbidden_actions_exposed"] is False
    assert result["actual_publish_performed"] is False
    assert result["pass"] is True
    assert Path(result["output_path"]).exists()
