from ai_objective_index import aoi_030a2_final_pypi_upload_runner as upload_runner
from ai_objective_index import aoi_030a2_final_pypi_verify as verify


def test_upload_runner_refuses_without_env():
    result = upload_runner.run_final_pypi_upload(
        execute=True,
        env={},
        gate_result={"decision": "PASS_READY_FOR_INTERACTIVE_TWINE_UPLOAD"},
        upload_runner=lambda command, timeout=900: {"ok": True},
        write_result=False,
    )

    assert result["decision"] == "HOLD_ENV_CONFIRM_REQUIRED"
    assert result["upload_performed"] is False
    assert "pypi-" not in str(result)


def test_upload_runner_never_logs_token_on_mock_success():
    result = upload_runner.run_final_pypi_upload(
        execute=True,
        env={upload_runner.CONFIRM_PYPI_ENV: "YES"},
        gate_result={"decision": "PASS_READY_FOR_INTERACTIVE_TWINE_UPLOAD"},
        upload_runner=lambda command, timeout=900: {"ok": True, "returncode": 0, "stdout": "", "stderr": ""},
        write_result=False,
    )

    assert result["decision"] == "UPLOAD_SUCCESS_DIRECT_TWINE_VERIFIED"
    assert result["token_printed"] is False


def test_pypi_verify_holds_when_upload_missing():
    result = verify.run_final_pypi_verify(upload_result={"decision": "HOLD_ENV_CONFIRM_REQUIRED"}, write_result=False)

    assert result["decision"] == "HOLD_PYPI_UPLOAD_NOT_CONFIRMED"


def test_pypi_verify_handles_package_not_found():
    def runner(command, timeout=300):
        text = " ".join(command)
        if "-m venv" in text:
            return {"ok": True, "returncode": 0, "stdout": "", "stderr": ""}
        if "pip install" in text:
            return {"ok": False, "returncode": 1, "stdout": "", "stderr": "No matching distribution found"}
        return {"ok": False, "returncode": 1, "stdout": "", "stderr": ""}

    result = verify.run_final_pypi_verify(
        upload_result={"decision": "UPLOAD_SUCCESS_DIRECT_TWINE_VERIFIED"},
        runner=runner,
        write_result=False,
    )

    assert result["decision"] == "HOLD_PYPI_NOT_PROPAGATED_OR_UPLOAD_MISSING"

