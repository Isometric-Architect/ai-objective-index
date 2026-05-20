from ai_objective_index.pypi_publish_readiness import run_pypi_publish_readiness


def test_pypi_publish_readiness_handles_missing_build_tool(monkeypatch):
    monkeypatch.setattr("ai_objective_index.pypi_publish_readiness._module_available", lambda name: False)
    result = run_pypi_publish_readiness(write_result=False)

    assert result["decision"] == "HOLD_BUILD_TOOL_MISSING"
    assert result["upload_performed"] is False


def test_pypi_publish_readiness_mocked_build_records_dist(monkeypatch):
    monkeypatch.setattr("ai_objective_index.pypi_publish_readiness._module_available", lambda name: name == "build")
    monkeypatch.setattr("ai_objective_index.pypi_publish_readiness._dist_files", lambda: [{"path": "dist/a.whl", "size_bytes": 10}])

    def runner(command, timeout=180):
        return {"ok": True, "stdout": "ok", "stderr": "", "command": command}

    result = run_pypi_publish_readiness(runner=runner, write_result=False)

    assert result["decision"] == "HOLD_TWINE_MISSING"
    assert result["dist_files"]
    assert result["pypi_upload_performed"] is False
