from __future__ import annotations

import argparse
import json
import os
import subprocess
from typing import Any, Callable

from .aoi_030a2_build_verify import sanitize
from .aoi_030a2_final_common import (
    CONFIRM_MCP_ENV,
    FINAL_MCP_GATE_PATH,
    FINAL_MCP_PUBLISH_PATH,
    now,
    read_json,
    repo_root,
    write_json,
)
from .aoi_030a2_final_mcp_registry_gate import SERVER_JSON, run_final_mcp_registry_gate
from .mcp_publisher_installer import find_mcp_publisher


PASS_GATE_DECISIONS = {
    "PASS_READY_FOR_MCP_REGISTRY_PUBLISH",
    "PASS_READY_FOR_MCP_REGISTRY_PUBLISH_ENV_REQUIRED",
}


def _run(command: list[str], timeout: int = 300) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": sanitize(exc)}
    return {
        "command": command,
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": sanitize(completed.stdout),
        "stderr": sanitize(completed.stderr),
    }


def _read_or_run_gate(env: dict[str, str] | None = None) -> dict[str, Any]:
    payload = read_json(FINAL_MCP_GATE_PATH)
    if payload.get("decision") == "PASS_READY_FOR_MCP_REGISTRY_PUBLISH_ENV_REQUIRED" and env and env.get(CONFIRM_MCP_ENV) == "YES":
        return run_final_mcp_registry_gate(env=env, write_result=True)
    if payload:
        return payload
    return run_final_mcp_registry_gate(env=env, write_result=True)


def _classify_failure(result: dict[str, Any]) -> str:
    combined = f"{result.get('stdout', '')}\n{result.get('stderr', '')}".lower()
    if "401" in combined or "unauthorized" in combined or "auth" in combined or "login" in combined:
        return "AUTH_REQUIRED"
    if "server_json_invalid" in combined or "server.json" in combined and "invalid" in combined:
        return "SERVER_JSON_INVALID"
    if "already" in combined or "exists" in combined:
        return "ALREADY_PUBLISHED_OR_VERSION_EXISTS"
    return "PUBLISH_FAILED"


def run_final_mcp_registry_publish(
    execute: bool = False,
    login_first: bool = False,
    env: dict[str, str] | None = None,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    publisher_finder: Callable[[], str] = find_mcp_publisher,
    gate_result: dict[str, Any] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    env_confirm_present = env_map.get(CONFIRM_MCP_ENV) == "YES"
    gate = gate_result if gate_result is not None else _read_or_run_gate(dict(env_map))
    publisher = publisher_finder()
    login_result: dict[str, Any] = {"skipped": True}
    publish_result: dict[str, Any] = {"skipped": True}
    submission_performed = False
    errors: list[str] = []
    warnings: list[str] = []

    if not execute:
        decision = "HOLD_EXECUTE_FLAG_REQUIRED"
        warnings.append("Use --execute only after explicit local confirmation.")
    elif not env_confirm_present:
        decision = "HOLD_ENV_CONFIRM_REQUIRED"
        warnings.append(f"{CONFIRM_MCP_ENV}=YES is required before registry publish.")
    elif gate.get("decision") not in PASS_GATE_DECISIONS:
        decision = "HOLD_MCP_GATE_NOT_PASS"
        warnings.append(f"MCP Registry gate is {gate.get('decision')}.")
    elif not publisher:
        decision = "HOLD_MCP_PUBLISHER_REQUIRED"
        warnings.append("mcp-publisher is not available.")
    else:
        if login_first:
            login_result = runner([publisher, "login", "github"], 300)
            if not login_result.get("ok"):
                decision = "AUTH_REQUIRED"
                warnings.append("mcp-publisher GitHub login did not complete.")
            else:
                publish_result = runner([publisher, "publish", str(SERVER_JSON)], 300)
                decision = "PASS_MCP_REGISTRY_PUBLISH_CONFIRMED" if publish_result.get("ok") else _classify_failure(publish_result)
        else:
            publish_result = runner([publisher, "publish", str(SERVER_JSON)], 300)
            decision = "PASS_MCP_REGISTRY_PUBLISH_CONFIRMED" if publish_result.get("ok") else _classify_failure(publish_result)

        if decision == "PASS_MCP_REGISTRY_PUBLISH_CONFIRMED":
            submission_performed = True
        elif decision == "AUTH_REQUIRED":
            warnings.append("Authentication is required. Run mcp-publisher login github locally, then retry.")
        elif decision == "SERVER_JSON_INVALID":
            errors.append("mcp-publisher reported server.json invalid.")
        elif decision == "ALREADY_PUBLISHED_OR_VERSION_EXISTS":
            warnings.append("Registry entry or version may already exist.")
        elif decision == "PUBLISH_FAILED":
            errors.append("mcp-publisher publish failed.")

    result = {
        "schema": "AOI_030A2FinalMCPRegistryPublishResult/v0.1",
        "generated_at": now(),
        "decision": decision,
        "gate_decision": gate.get("decision"),
        "env_confirm_present": env_confirm_present,
        "execute_requested": execute,
        "login_first": login_first,
        "mcp_publisher_path": publisher,
        "login_result": login_result,
        "publish_result": publish_result,
        "submission_performed": submission_performed,
        "token_printed": False,
        "pypi_upload_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(FINAL_MCP_PUBLISH_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--login", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_final_mcp_registry_publish(execute=args.execute, login_first=args.login)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(
            "aoi_030a2_final_mcp_registry_publish: "
            f"{result['decision']} submission_performed={result['submission_performed']}"
        )


if __name__ == "__main__":
    main()

