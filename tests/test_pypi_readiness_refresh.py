from ai_objective_index import pypi_readiness_refresh


def test_pypi_readiness_refresh_build_ready_holds_for_testpypi(monkeypatch):
    def fake_read(path):
        name = str(path)
        if "PACKAGE_METADATA" in name:
            return {"overall_token": "PASS"}
        if "DIST_BUILD" in name:
            return {"decision": "PASS_BUILD_READY", "dist_files": [{"path": "dist/a.whl"}]}
        if "TWINE_CHECK" in name:
            return {"decision": "PASS_TWINE_CHECK"}
        if "LOCAL_INSTALL" in name:
            return {"decision": "PASS_LOCAL_INSTALL_SMOKE"}
        return {}

    monkeypatch.setattr(pypi_readiness_refresh, "_read_json", fake_read)
    result = pypi_readiness_refresh.run_pypi_readiness_refresh(write_result=False)

    assert result["decision"] == "HOLD_TESTPYPI_ACCOUNT_REQUIRED"
    assert result["testpypi_upload_performed"] is False


def test_pypi_readiness_refresh_build_missing_holds(monkeypatch):
    def fake_read(path):
        name = str(path)
        if "PYPI_PUBLISH" in name:
            return {"decision": "HOLD_BUILD_TOOL_MISSING"}
        return {}

    monkeypatch.setattr(pypi_readiness_refresh, "_read_json", fake_read)
    result = pypi_readiness_refresh.run_pypi_readiness_refresh(write_result=False)

    assert result["decision"] == "HOLD_BUILD_TOOL_MISSING"
