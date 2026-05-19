from ai_objective_index import deployment_push_sync as push


def test_deployment_push_sync_dry_run_does_not_commit_or_push():
    result = push.run_deployment_push_sync(execute=False, write_result=False, stage_paths=[])

    assert result["dry_run"] is True
    assert result["committed"] is False
    assert result["pushed"] is False


def test_deployment_push_sync_execute_can_be_mocked(monkeypatch):
    commands = []

    def fake_runner(command, timeout):
        commands.append(command)
        if "diff" in command:
            return {"ok": False, "returncode": 1, "stdout": "", "stderr": ""}
        if "rev-parse" in command:
            return {"ok": True, "returncode": 0, "stdout": "abc123", "stderr": ""}
        if "status" in command:
            return {"ok": True, "returncode": 0, "stdout": "", "stderr": ""}
        if "branch" in command:
            return {"ok": True, "returncode": 0, "stdout": "main", "stderr": ""}
        if "remote" in command:
            return {"ok": True, "returncode": 0, "stdout": "https://github.com/Isometric-Architect/ai-objective-index.git", "stderr": ""}
        return {"ok": True, "returncode": 0, "stdout": "", "stderr": ""}

    monkeypatch.setattr(push, "_minimum_checks", lambda: (True, [], {"mock": "PASS"}))
    monkeypatch.setattr(push, "_safe_existing_paths", lambda paths=None: ["README.md"])

    result = push.run_deployment_push_sync(execute=True, runner=fake_runner, write_result=False)

    assert result["committed"] is True
    assert result["pushed"] is True
    assert result["visibility_changed"] is False
    assert not any("--force" in part for command in commands for part in command)
    assert "token" not in str(result).lower()
