from pathlib import Path

from ai_objective_index.public_observation_runner import run_public_observation_phase
from ai_objective_index.residual_worktree_review import run_residual_worktree_review


def test_package_8n_assets_exist():
    run_public_observation_phase("0h", write_result=True)
    run_residual_worktree_review(status_text="", write_result=True)

    assert Path("docs/package_8n_public_observation_runner.md").exists()
    assert Path("docs/public_observation_runner.md").exists()
    assert Path("docs/residual_worktree_review_policy.md").exists()
    assert Path("public_ops/observation").exists()
    assert Path("public_ops/residual_review").exists()
