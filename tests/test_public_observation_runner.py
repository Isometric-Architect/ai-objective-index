from pathlib import Path

from ai_objective_index.public_observation_runner import run_public_observation_phase


def test_public_observation_runner_phase_0h_creates_active_log():
    result = run_public_observation_phase("0h", write_result=True)

    assert result["phase"] == "0h"
    assert result["community_post_performed"] is False
    assert result["github_release_created"] is False
    assert Path("public_ops/observation/OBSERVATION_LOG_72H_ACTIVE.md").exists()


def test_public_observation_runner_phase_24h_template():
    result = run_public_observation_phase("24h", write_result=True)

    assert result["phase"] == "24h"
    assert result["actual_publish_performed"] is False
    assert Path("public_ops/observation/OBSERVATION_SNAPSHOT_24H.template.json").exists()
