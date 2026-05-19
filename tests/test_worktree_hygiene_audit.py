from pathlib import Path

from ai_objective_index.worktree_hygiene_audit import classify_path, run_worktree_hygiene_audit


def test_worktree_hygiene_classifies_cache_and_tokens():
    assert classify_path("__pycache__/x.pyc") == "should_ignore"
    assert classify_path(".pytest_cache/v/cache/nodeids") == "should_ignore"
    assert classify_path(".env") == "do_not_commit"
    assert classify_path("token.txt") == "do_not_commit"
    assert classify_path("docs/token_revocation_public_stage.md") == "safe_to_commit_later"


def test_worktree_hygiene_writes_outputs_without_deleting_files():
    result = run_worktree_hygiene_audit(status_text="?? .env\n M README.md\n?? __pycache__/x.pyc\n", write_result=True)

    assert result["overall_token"] == "BLOCK"
    assert result["deleted_files"] == []
    assert Path("public_ops/WORKTREE_HYGIENE_AUDIT_v0_1.json").exists()
    assert Path("public_ops/WORKTREE_CLASSIFICATION.md").exists()

