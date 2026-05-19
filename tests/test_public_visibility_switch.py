from ai_objective_index import public_visibility_switch as switch


class FakeApi:
    def __init__(self):
        self.updated = []

    def whoami(self):
        return {"name": "edict-lab"}

    def update_repo_visibility(self, repo_id, repo_type, private):
        self.updated.append((repo_id, repo_type, private))


def test_public_visibility_switch_dry_run_does_not_change_visibility():
    result = switch.run_public_visibility_switch(execute=False, api=FakeApi(), write_result=False)

    assert result["dry_run"] is True
    assert result["public_switch_performed"] is False
    assert result["github_visibility_changed"] is False


def test_public_visibility_switch_execute_without_env_refuses():
    result = switch.run_public_visibility_switch(execute=True, api=FakeApi(), env={}, write_result=False)

    assert result["public_switch_performed"] is False
    assert result["errors"]
    assert "hf_fake_token" not in str(result).lower()


def test_public_visibility_switch_execute_with_mocked_auth_and_env(monkeypatch):
    api = FakeApi()

    monkeypatch.setattr(switch, "run_public_launch_gate", lambda write_result=True: {"overall_token": "PASS"})

    def fake_runner(command, timeout):
        assert "--force" not in command
        return {"ok": True, "stdout": "", "stderr": "", "returncode": 0}

    result = switch.run_public_visibility_switch(
        execute=True,
        api=api,
        command_runner=fake_runner,
        env={switch.CONFIRM_ENV: switch.CONFIRM_VALUE},
        write_result=False,
    )

    assert result["github_visibility_changed"] is True
    assert result["hf_space_visibility_changed"] is True
    assert result["hf_dataset_visibility_changed"] is True
    assert result["public_switch_performed"] is True
    assert "hf_fake_token" not in str(result).lower()
