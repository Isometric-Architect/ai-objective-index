from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Callable

from .aoi_030a2_final_common import (
    CONFIRM_PYPI_ENV,
    FINAL_PYPI_UPLOAD_GATE_PATH,
    FINAL_PYPI_UPLOAD_PATH,
    PACKAGE_NAME,
    SDIST_PATH,
    TARGET_VERSION,
    WHEEL_PATH,
    now,
    read_json,
    repo_root,
    write_json,
)
from .aoi_030a2_final_pypi_upload_gate import run_final_pypi_upload_gate


def upload_command() -> list[str]:
    return [sys.executable, "-m", "twine", "upload", str(WHEEL_PATH), str(SDIST_PATH)]


def _interactive_upload(command: list[str], timeout: int = 900) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, cwd=repo_root(), timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "returncode": None, "error": str(exc)[:400], "stdout": "", "stderr": ""}
    return {"ok": completed.returncode == 0, "returncode": completed.returncode, "stdout": "", "stderr": ""}


def _read_or_run_gate() -> dict[str, Any]:
    payload = read_json(FINAL_PYPI_UPLOAD_GATE_PATH)
    if payload:
        return payload
    return run_final_pypi_upload_gate(write_result=True)


def run_final_pypi_upload(
    execute: bool = False,
    env: dict[str, str] | None = None,
    upload_runner: Callable[[list[str], int], dict[str, Any]] = _interactive_upload,
    gate_result: dict[str, Any] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    gate = gate_result if gate_result is not None else _read_or_run_gate()
    env_confirm_present = env_map.get(CONFIRM_PYPI_ENV) == "YES"
    upload_result: dict[str, Any] = {"skipped": True, "ok": False}
    upload_performed = False
    errors: list[str] = []
    warnings: list[str] = []

    if not execute:
        decision = "HOLD_EXECUTE_FLAG_REQUIRED"
        warnings.append("Use --execute only after explicit local confirmation.")
    elif not env_confirm_present:
        decision = "HOLD_ENV_CONFIRM_REQUIRED"
        warnings.append(f"{CONFIRM_PYPI_ENV}=YES is required before upload.")
    elif gate.get("decision") != "PASS_READY_FOR_INTERACTIVE_TWINE_UPLOAD":
        decision = "HOLD_UPLOAD_GATE_NOT_PASS"
        warnings.append(f"Upload gate is {gate.get('decision')}.")
    else:
        upload_result = upload_runner(upload_command(), 900)
        if upload_result.get("ok"):
            decision = "UPLOAD_SUCCESS_DIRECT_TWINE_VERIFIED"
            upload_performed = True
        else:
            combined = f"{upload_result.get('stdout', '')}\n{upload_result.get('stderr', '')}\n{upload_result.get('error', '')}".lower()
            if "already" in combined or "exists" in combined or "400" in combined:
                decision = "HOLD_VERSION_ALREADY_EXISTS"
                warnings.append("Twine reported that the version or files may already exist.")
            else:
                decision = "BLOCK_UPLOAD_FAILED"
                errors.append("Interactive twine upload returned a non-zero status.")

    result = {
        "schema": "AOI_030A2FinalPyPIUploadResult/v0.1",
        "generated_at": now(),
        "decision": decision,
        "target_version": TARGET_VERSION,
        "package_name": PACKAGE_NAME,
        "gate_decision": gate.get("decision"),
        "env_confirm_present": env_confirm_present,
        "execute_requested": execute,
        "command_redacted": " ".join(upload_command()),
        "upload_result": upload_result,
        "upload_performed": upload_performed,
        "token_printed": False,
        "token_stored": False,
        "pypirc_created": False,
        "mcp_registry_publish_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(FINAL_PYPI_UPLOAD_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_final_pypi_upload(execute=args.execute)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(
            "aoi_030a2_final_pypi_upload_runner: "
            f"{result['decision']} upload_performed={result['upload_performed']} token_printed=False"
        )


if __name__ == "__main__":
    main()

