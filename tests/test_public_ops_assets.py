from pathlib import Path

from ai_objective_index.github_issue_labels import write_labels_plan
from ai_objective_index.observation_log import create_observation_assets


def test_public_ops_assets_exist():
    write_labels_plan()
    create_observation_assets()

    assert Path("docs/package_8m_public_ops_baseline.md").exists()
    assert Path("docs/worktree_hygiene_policy.md").exists()
    assert Path("docs/github_issue_loop_operations.md").exists()
    assert Path("docs/public_metrics_baseline.md").exists()
    assert Path("public_ops/GITHUB_ISSUE_LABELS_PLAN.md").exists()
    assert Path("public_ops/OBSERVATION_LOG_72H.md").exists()
