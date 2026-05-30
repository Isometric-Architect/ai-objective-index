import json

from ai_objective_index.agent_discovery_eval.pypi_public_install_smoke import run_pypi_public_install_smoke


def test_pypi_public_install_smoke_passes_with_mocked_runner():
    def runner(command, timeout, cwd):
        if "-c" in command:
            return {
                "command": command,
                "ok": True,
                "returncode": 0,
                "stdout": json.dumps(
                    {
                        "version": "0.3.0a2",
                        "agent_adoption_imported": True,
                        "capability_card_version": "0.3.0a2",
                        "capability_card_packaged": True,
                        "agent_schema_packaged": True,
                        "agent_examples_packaged": True,
                        "api_examples_packaged": True,
                    }
                ),
                "stderr": "",
            }
        return {"command": command, "ok": True, "returncode": 0, "stdout": "", "stderr": ""}

    result = run_pypi_public_install_smoke(runner=runner, write_result=False)

    assert result["decision"] == "PASS_PYPI_PUBLIC_INSTALL_SMOKE"
    assert result["verification_payload"]["version"] == "0.3.0a2"


def test_pypi_public_install_smoke_holds_on_install_failure():
    def runner(command, timeout, cwd):
        return {"command": command, "ok": False, "returncode": 1, "stdout": "", "stderr": "offline"}

    result = run_pypi_public_install_smoke(runner=runner, write_result=False)

    assert result["decision"] == "HOLD_PUBLIC_PYPI_NOT_READY"
