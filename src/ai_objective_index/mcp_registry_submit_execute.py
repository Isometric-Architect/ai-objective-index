from __future__ import annotations

import json
import os
import subprocess
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .mcp_publisher_installer import find_mcp_publisher, redact_token_like
from .mcp_registry_publish_preflight import run_mcp_registry_publish_preflight
from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "wave13_mcp_registry_submit" / "MCP_REGISTRY_SUBMIT_RESULT.json"
CONFIRM_ENV = "AOI_MCP_REGISTRY_SUBMIT_CONFIRM"
SERVER_JSON = ".mcp/server.json"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _run_command(command: list[str], timeout: int = 300) -> dict[str, Any]:
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
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": redact_token_like(exc)}
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": redact_token_like(completed.stdout),
        "stderr": redact_token_like(completed.stderr),
    }


def _planned_command(binary: str | None = None) -> list[str]:
    return [binary or "mcp-publisher", "publish", SERVER_JSON]


def run_mcp_registry_submit_execute(
    execute: bool = False,
    env: dict[str, str] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    preflight = run_mcp_registry_publish_preflight(write_result=False)
    publisher = find_mcp_publisher()
    command = _planned_command(publisher or None)
    errors: list[str] = []
    warnings: list[str] = []
    dry_run_result: dict[str, Any] = {}
    publish_result: dict[str, Any] = {}
    submission_performed = False

    if not execute:
        result_token = "DRY_RUN_ONLY"
        if preflight.get("decision") != "PASS_READY_TO_SUBMIT":
            warnings.append(f"Dry-run only; preflight is {preflight.get('decision')}.")
        elif publisher:
            dry_run_command = [publisher, "publish", "--dry-run", SERVER_JSON]
            dry_run_result = _run_command(dry_run_command, timeout=120)
            if not dry_run_result.get("ok"):
                warnings.append("DRY_RUN_COMMAND_NOT_SUPPORTED or dry-run validation failed; no publish attempted.")
        warnings.append("No MCP Registry submission performed in dry-run mode.")
    elif preflight.get("decision") != "PASS_READY_TO_SUBMIT":
        result_token = "BLOCK_PREFLIGHT_FAILED"
        errors.append("Publish preflight is not PASS_READY_TO_SUBMIT.")
    elif env_map.get(CONFIRM_ENV) != "YES":
        result_token = "HOLD_ENV_CONFIRM_REQUIRED"
        warnings.append(f"{CONFIRM_ENV}=YES is required before submit.")
    elif not publisher:
        result_token = "HOLD_LOGIN_REQUIRED"
        warnings.append("mcp-publisher is not available.")
    else:
        publish_result = _run_command(command, timeout=300)
        combined = f"{publish_result.get('stdout', '')}\n{publish_result.get('stderr', '')}".lower()
        if publish_result.get("ok"):
            result_token = "PUBLISH_SUCCESS"
            submission_performed = True
        elif "already" in combined or "exists" in combined:
            result_token = "HOLD_ALREADY_PUBLISHED_OR_VERSION_EXISTS"
            warnings.append("Registry entry or version appears to already exist.")
        else:
            result_token = "BLOCK_PUBLISH_FAILED"
            errors.append("mcp-publisher publish failed.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "env_confirm_present": env_map.get(CONFIRM_ENV) == "YES",
        "submission_performed": submission_performed,
        "command_redacted": " ".join(command),
        "dry_run_result": dry_run_result,
        "publish_result": publish_result,
        "preflight_decision": preflight.get("decision"),
        "result_token": result_token,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    result = run_mcp_registry_submit_execute(execute=args.execute)
    print(
        "mcp_registry_submit_execute: "
        f"{result['result_token']} submission_performed={result['submission_performed']}"
    )


if __name__ == "__main__":
    main()
