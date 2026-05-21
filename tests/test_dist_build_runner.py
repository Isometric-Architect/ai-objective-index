from ai_objective_index import dist_build_runner


def test_dist_build_runner_mocked_build_success_records_dist(monkeypatch):
    commands = []
    monkeypatch.setattr(dist_build_runner, "_current_version", lambda: "0.3.0a1")
    monkeypatch.setattr(dist_build_runner, "_module_available", lambda name: True)
    monkeypatch.setattr(dist_build_runner, "_remove_old_aoi_dist_artifacts", lambda: [])
    monkeypatch.setattr(
        dist_build_runner,
        "_dist_files",
        lambda: [
            {"path": "dist/ai_objective_index-0.3.0a1-py3-none-any.whl", "size_bytes": 100},
            {"path": "dist/ai_objective_index-0.3.0a1.tar.gz", "size_bytes": 100},
        ],
    )

    def runner(command, timeout=300):
        commands.append(command)
        return {"ok": True, "stdout": "ok", "stderr": "", "command": command}

    result = dist_build_runner.run_dist_build(runner=runner, write_result=False)

    assert result["decision"] == "PASS_BUILD_READY"
    assert len(result["dist_files"]) == 2
    assert not any("upload" in " ".join(command) for command in commands)


def test_dist_build_runner_twine_failure_blocks(monkeypatch):
    monkeypatch.setattr(dist_build_runner, "_current_version", lambda: "0.3.0a1")
    monkeypatch.setattr(dist_build_runner, "_module_available", lambda name: True)
    monkeypatch.setattr(dist_build_runner, "_remove_old_aoi_dist_artifacts", lambda: [])
    monkeypatch.setattr(
        dist_build_runner,
        "_dist_files",
        lambda: [
            {"path": "dist/ai_objective_index-0.3.0a1-py3-none-any.whl", "size_bytes": 100},
            {"path": "dist/ai_objective_index-0.3.0a1.tar.gz", "size_bytes": 100},
        ],
    )

    def runner(command, timeout=300):
        if "twine" in command:
            return {"ok": False, "stdout": "", "stderr": "bad metadata", "command": command}
        return {"ok": True, "stdout": "ok", "stderr": "", "command": command}

    result = dist_build_runner.run_dist_build(runner=runner, write_result=False)

    assert result["decision"] == "BLOCK_TWINE_CHECK_FAILED"
    assert result["upload_performed"] is False


def test_dist_build_runner_version_mismatch_blocks(monkeypatch):
    monkeypatch.setattr(dist_build_runner, "_current_version", lambda: "0.2.0")
    result = dist_build_runner.run_dist_build(write_result=False)

    assert result["decision"] == "BLOCK_VERSION_MISMATCH"
    assert result["upload_performed"] is False
