from pathlib import Path

from ai_objective_index import local_install_smoke


def test_local_install_smoke_mocked_success(monkeypatch):
    root = Path.cwd()
    monkeypatch.setattr(local_install_smoke, "_wheel_path", lambda: root / "dist" / "ai_objective_index-0.3.0a1-py3-none-any.whl")

    def create_venv(path):
        (path / "Scripts").mkdir(parents=True, exist_ok=True)

    def runner(command, timeout=300, cwd=None):
        return {"ok": True, "stdout": "ok", "stderr": "", "command": command}

    result = local_install_smoke.run_local_install_smoke(
        runner=runner,
        create_venv=create_venv,
        cleanup=True,
        write_result=False,
    )

    assert result["decision"] == "PASS_LOCAL_INSTALL_SMOKE"
    assert result["network_required"] is False
    assert result["upload_performed"] is False
