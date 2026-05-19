from ai_objective_index.github_issue_labels import run_github_issue_labels


def test_github_issue_labels_dry_run_does_not_call_gh():
    calls = []

    def runner(command, timeout):
        calls.append(command)
        return {"ok": True, "stdout": "", "stderr": "", "returncode": 0}

    result = run_github_issue_labels(execute=False, runner=runner, write_result=False)

    assert result["dry_run"] is True
    assert calls == []
    assert result["token_printed"] is False


def test_github_issue_labels_execute_mocked_duplicate_safe(monkeypatch):
    monkeypatch.setattr("ai_objective_index.github_issue_labels._gh_available", lambda: True)

    def runner(command, timeout):
        if command[:3] == ["gh", "auth", "status"]:
            return {"ok": True, "stdout": "", "stderr": "", "returncode": 0}
        if command[:3] == ["gh", "label", "create"]:
            return {"ok": False, "stdout": "", "stderr": "already exists", "returncode": 1}
        if command[:3] == ["gh", "label", "edit"]:
            return {"ok": True, "stdout": "", "stderr": "", "returncode": 0}
        return {"ok": True, "stdout": "", "stderr": "", "returncode": 0}

    result = run_github_issue_labels(execute=True, runner=runner, write_result=False)

    assert result["execute"] is True
    assert result["errors"] == []
    assert result["labels_created_or_existing"]
    assert result["token_printed"] is False

