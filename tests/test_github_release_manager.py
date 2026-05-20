import json
from pathlib import Path

from ai_objective_index.github_release_manager import run_github_release_manager


def test_github_release_manager_dry_run_creates_notes_and_result():
    result = run_github_release_manager(execute=False, write_result=True)
    notes = Path("public_launch/wave1/GITHUB_RELEASE_NOTES_v0_2_0_public_beta.md").read_text(encoding="utf-8").lower()

    assert result["release_created"] is False
    assert result["dry_run"] is True
    assert "not verified" in notes
    assert "not security certified" in notes
    assert "not a quality guarantee" in notes
    assert "token" not in json.dumps(result).lower() or result["token_printed"] is False


def test_github_release_manager_execute_mocked(monkeypatch):
    commands = []

    def runner(command, timeout=120):
        commands.append(command)
        if command[:3] == ["gh", "auth", "status"]:
            return {"ok": True, "stdout": "", "stderr": ""}
        if command[:3] == ["gh", "release", "view"]:
            return {"ok": False, "stdout": "", "stderr": "not found"}
        if command[:3] == ["gh", "release", "create"]:
            return {"ok": True, "stdout": "https://github.com/release", "stderr": ""}
        return {"ok": True, "stdout": "", "stderr": ""}

    monkeypatch.setattr("ai_objective_index.github_release_manager._gh_available", lambda: True)
    result = run_github_release_manager(execute=True, runner=runner, write_result=False)

    assert result["release_created"] is True
    assert "--clobber" not in " ".join(" ".join(command) for command in commands)
    assert result["token_printed"] is False
