from pathlib import Path

from ai_objective_index import prepublic_sync


def _fake_git_runner(command, timeout):
    joined = " ".join(command)
    assert "--force" not in command
    assert "--force-with-lease" not in command
    if "status --short" in joined:
        return {"ok": True, "returncode": 0, "stdout": " M README.md", "stderr": "", "command": command}
    if "branch --show-current" in joined:
        return {"ok": True, "returncode": 0, "stdout": "main", "stderr": "", "command": command}
    if "remote get-url origin" in joined:
        return {"ok": True, "returncode": 0, "stdout": "https://github.com/Isometric-Architect/ai-objective-index", "stderr": "", "command": command}
    if "diff --cached --quiet" in joined:
        return {"ok": False, "returncode": 1, "stdout": "", "stderr": "", "command": command}
    if "commit -m" in joined:
        return {"ok": True, "returncode": 0, "stdout": "[main abc123] commit", "stderr": "", "command": command}
    if "rev-parse HEAD" in joined:
        return {"ok": True, "returncode": 0, "stdout": "abc123", "stderr": "", "command": command}
    if "push -u origin main" in joined:
        return {"ok": True, "returncode": 0, "stdout": "pushed", "stderr": "", "command": command}
    return {"ok": True, "returncode": 0, "stdout": "", "stderr": "", "command": command}


def test_prepublic_sync_dry_run_does_not_commit_or_push():
    result = prepublic_sync.run_prepublic_sync(
        execute=False,
        runner=_fake_git_runner,
        stage_paths=["README.md"],
        write_result=True,
    )

    assert result["dry_run"] is True
    assert result["committed"] is False
    assert result["pushed"] is False
    assert result["github_visibility_changed"] is False
    assert Path("public_launch/PREPUBLIC_SYNC_RESULT.json").exists()


def test_prepublic_sync_execute_can_be_mocked(monkeypatch):
    monkeypatch.setattr(prepublic_sync, "_minimum_checks", lambda: (True, [], {"mock": "PASS"}))
    monkeypatch.setattr(
        prepublic_sync,
        "run_final_public_dry_run",
        lambda write_result=True: {"overall_token": "PASS"},
    )
    result = prepublic_sync.run_prepublic_sync(
        execute=True,
        runner=_fake_git_runner,
        stage_paths=["README.md"],
        write_result=False,
    )

    assert result["committed"] is True
    assert result["pushed"] is True
    assert result["force_push_used"] is False
    assert result["github_visibility_changed"] is False
    assert result["hf_visibility_changed"] is False
