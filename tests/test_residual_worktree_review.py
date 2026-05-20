from pathlib import Path

from ai_objective_index.residual_worktree_review import classify_residual_path, run_residual_worktree_review


def test_residual_worktree_review_classifies_cache_and_sensitive_paths():
    assert classify_residual_path("__pycache__/x.pyc") == "safe_to_ignore"
    assert classify_residual_path(".pytest_cache/v/cache/nodeids") == "safe_to_ignore"
    assert classify_residual_path("token.txt") == "possible_sensitive"
    assert classify_residual_path("docs/token_revocation_public_stage.md") == "candidate_for_future_commit"


def test_residual_worktree_review_writes_plans_without_deleting():
    result = run_residual_worktree_review(
        status_text="?? __pycache__/x.pyc\n?? token.txt\n M docs/example.md\n",
        write_result=True,
    )

    assert result["overall_token"] == "BLOCK"
    assert result["deleted_files"] == []
    assert result["git_add_all_used"] is False
    assert Path("public_ops/residual_review/RESIDUAL_WORKTREE_REVIEW.md").exists()
    assert Path("public_ops/residual_review/RESIDUAL_COMMIT_PLAN.md").exists()
    assert Path("public_ops/residual_review/RESIDUAL_IGNORE_PLAN.md").exists()
    assert Path("public_ops/residual_review/RESIDUAL_USER_REVIEW_LIST.md").exists()
