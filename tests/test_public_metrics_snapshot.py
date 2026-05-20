from pathlib import Path

from ai_objective_index.public_metrics_snapshot import run_public_metrics_snapshot


def _missing_runner(command, timeout=30):
    return {"ok": False, "returncode": 1, "stdout": "", "stderr": "not available"}


def test_public_metrics_snapshot_handles_api_unavailable():
    result = run_public_metrics_snapshot(runner=_missing_runner, write_result=True)

    assert result["github"]["stars_count"] == "not_checked"
    assert result["community_post_performed"] is False
    assert result["github_release_created"] is False
    assert result["mcp_registry_submission_performed"] is False
    assert Path("public_ops/observation/OBSERVATION_SNAPSHOT_0H.json").exists()
    assert Path("public_ops/observation/PUBLIC_METRICS_SNAPSHOT_0H.md").exists()
