from ai_objective_index import final_public_dry_run as dry_run


def _runner(command, timeout):
    return {
        "ok": True,
        "returncode": 0,
        "stdout": "https://github.com/Isometric-Architect/ai-objective-index",
        "stderr": "",
    }


def test_final_public_dry_run_has_switch_guard_fields():
    result = dry_run.run_final_public_dry_run(
        write_result=False,
        runner=_runner,
        run_live_helpers=False,
    )

    assert result["overall_token"] in {"PASS", "HOLD", "BLOCK"}
    assert result["actual_switch_performed"] is False
    assert result["required_user_confirmation"] is True
    assert result["required_env_for_execute"] == "AOI_PUBLIC_LAUNCH_CONFIRM=YES"
    assert result["would_switch"]["github_repo"] is True
    assert result["would_switch"]["hf_space"] is True
    assert result["would_switch"]["hf_dataset"] is True


def test_final_public_dry_run_missing_no_contact_gate_holds(monkeypatch):
    monkeypatch.setattr(dry_run, "_read_json", lambda path: {})
    monkeypatch.setattr(dry_run, "_public_beta_mcp_count", lambda: 50)
    result = dry_run.run_final_public_dry_run(
        write_result=False,
        runner=_runner,
        run_live_helpers=False,
    )

    assert result["checks"]["no_contact_launch_gate"]["token"] == "HOLD"
    assert result["overall_token"] in {"HOLD", "BLOCK"}
