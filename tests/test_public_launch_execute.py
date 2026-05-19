import re

from ai_objective_index import public_launch_execute as execute


def _runner(command, timeout):
    return {"ok": True, "returncode": 0, "stdout": "ok", "stderr": "", "command": command}


class MockApi:
    def __init__(self):
        self.calls = []

    def whoami(self):
        return {"name": "edict-lab"}

    def update_repo_visibility(self, repo_id, repo_type, private):
        self.calls.append((repo_id, repo_type, private))


def test_public_launch_execute_dry_run_does_not_switch(monkeypatch):
    monkeypatch.setattr(execute, "_required_checks", lambda: (True, [], {"mock": "PASS"}))
    result = execute.run_public_launch_execute(execute=False, command_runner=_runner, write_result=False)

    assert result["dry_run"] is True
    assert result["public_switch_performed"] is False
    assert result["github_visibility_changed"] is False


def test_public_launch_execute_without_env_refuses(monkeypatch):
    monkeypatch.setattr(execute, "_required_checks", lambda: (True, [], {"mock": "PASS"}))
    result = execute.run_public_launch_execute(
        execute=True,
        env={},
        command_runner=_runner,
        api=MockApi(),
        write_result=False,
    )

    assert result["env_confirm_present"] is False
    assert result["public_switch_performed"] is False
    assert result["errors"]


def test_public_launch_execute_mocked_success(monkeypatch):
    monkeypatch.setattr(execute, "_required_checks", lambda: (True, [], {"mock": "PASS"}))
    monkeypatch.setattr(execute, "check_hf_auth", lambda api=None, write_result=True: {"authenticated": True})
    monkeypatch.setattr(execute.shutil, "which", lambda name: "gh")
    api = MockApi()

    result = execute.run_public_launch_execute(
        execute=True,
        env={"AOI_PUBLIC_LAUNCH_CONFIRM": "YES"},
        command_runner=_runner,
        api=api,
        write_result=False,
    )

    assert result["github_visibility_changed"] is True
    assert result["hf_space_visibility_changed"] is True
    assert result["hf_dataset_visibility_changed"] is True
    assert result["public_switch_performed"] is True
    assert result["token_printed"] is False
    result_text = str(result)
    assert "ghp_" not in result_text
    assert "gho_" not in result_text
    assert re.search(r"hf_[A-Za-z0-9]{20,}", result_text) is None
