import json

from ai_objective_index import local_build_tools


def test_local_build_tools_check_mode_does_not_install(monkeypatch):
    calls = []
    monkeypatch.setattr(local_build_tools, "module_available", lambda name: False)

    def runner(command, timeout=300):
        calls.append(command)
        return {"ok": True, "stdout": "", "stderr": ""}

    result = local_build_tools.run_local_build_tools(install=False, runner=runner, write_result=False)

    assert result["install_attempted"] is False
    assert calls == []
    assert result["token_printed"] is False


def test_local_build_tools_install_path_records_attempt(monkeypatch):
    monkeypatch.setattr(local_build_tools, "module_available", lambda name: True)

    def runner(command, timeout=300):
        return {"ok": True, "stdout": "installed", "stderr": "", "command": command}

    result = local_build_tools.run_local_build_tools(install=True, runner=runner, write_result=False)

    assert result["install_attempted"] is True
    assert result["install_result"]["ok"] is True
    assert result["token_printed"] is False
    assert "pypi-" not in json.dumps(result).lower()
