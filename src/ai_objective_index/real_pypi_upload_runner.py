from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .real_pypi_upload_gate import OUTPUT_PATH as GATE_OUTPUT_PATH
from .real_pypi_upload_gate import SDIST_PATH, TARGET_VERSION, WHEEL_PATH, _repo_root, _sanitize, evaluate_real_pypi_upload_gate


OUTPUT_PATH = Path("public_launch") / "wave10_real_pypi" / "REAL_PYPI_UPLOAD_RESULT.json"
PYPI_PROJECT_URL = f"https://pypi.org/project/ai-objective-index/{TARGET_VERSION}/"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def upload_command() -> list[str]:
    return [sys.executable, "-m", "twine", "upload", str(WHEEL_PATH), str(SDIST_PATH)]


def _run(command: list[str], timeout: int = 600) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=_repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": _sanitize(completed.stdout),
            "stderr": _sanitize(completed.stderr),
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": _sanitize(exc)}


def _sanitize_upload_result(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(payload)
    if "stdout" in sanitized:
        sanitized["stdout"] = _sanitize(sanitized.get("stdout"))
    if "stderr" in sanitized:
        sanitized["stderr"] = _sanitize(sanitized.get("stderr"))
    return sanitized


def run_real_pypi_upload(
    execute: bool = False,
    env: dict[str, str] | None = None,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
) -> dict[str, Any]:
    env = env or os.environ
    command = upload_command()
    command_redacted = " ".join(command)
    errors: list[str] = []
    warnings: list[str] = []
    env_confirm_present = env.get("AOI_REAL_PYPI_UPLOAD_CONFIRM") == "YES"
    gate = _read_json(GATE_OUTPUT_PATH) or evaluate_real_pypi_upload_gate(write_result=True)

    if not execute:
        result_token = "DRY_RUN_ONLY"
        upload_result: dict[str, Any] = {"ok": False, "skipped": True}
        upload_performed = False
    elif not env_confirm_present:
        result_token = "HOLD_ENV_CONFIRM_REQUIRED"
        upload_result = {"ok": False, "skipped": True}
        upload_performed = False
        warnings.append("Set AOI_REAL_PYPI_UPLOAD_CONFIRM=YES before executing.")
    elif gate.get("decision") != "PASS_READY_FOR_REAL_PYPI_UPLOAD":
        result_token = "BLOCK_UPLOAD_FAILED"
        upload_result = {"ok": False, "skipped": True, "gate_decision": gate.get("decision")}
        upload_performed = False
        errors.append(f"Gate is not PASS_READY_FOR_REAL_PYPI_UPLOAD: {gate.get('decision')}")
    else:
        upload_result = _sanitize_upload_result(runner(command, 900))
        text = (str(upload_result.get("stdout", "")) + "\n" + str(upload_result.get("stderr", ""))).lower()
        upload_performed = bool(upload_result.get("ok"))
        if upload_result.get("ok"):
            result_token = "UPLOAD_SUCCESS"
        elif "already exist" in text or "file already exists" in text or "400" in text and "already" in text:
            result_token = "HOLD_ALREADY_EXISTS"
            warnings.append("PyPI reported an existing file or version; do not retry same files blindly.")
        elif "unauthorized" in text or "403" in text or "401" in text or "invalid or non-existent authentication" in text:
            result_token = "HOLD_AUTH_FAILED"
            warnings.append("PyPI authentication failed. Recheck token locally; do not paste it into chat.")
        else:
            result_token = "BLOCK_UPLOAD_FAILED"
            errors.append("twine upload failed.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "env_confirm_present": env_confirm_present,
        "upload_performed": upload_performed,
        "command_redacted": command_redacted,
        "upload_result": upload_result,
        "token_printed": False,
        "pypi_project_url": PYPI_PROJECT_URL if result_token in {"UPLOAD_SUCCESS", "HOLD_ALREADY_EXISTS"} else "",
        "result_token": result_token,
        "errors": errors,
        "warnings": warnings,
        "testpypi_used": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Dry-run or execute real PyPI upload through interactive twine prompts.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    result = run_real_pypi_upload(execute=bool(args.execute))
    print(
        "real_pypi_upload_runner: "
        f"{result['result_token']} "
        f"upload_performed={result['upload_performed']} "
        "token_printed=False"
    )


if __name__ == "__main__":
    main()
