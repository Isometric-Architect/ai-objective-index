from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .aoi_030a2_build_verify import sanitize
from .aoi_030a2_marker_sync import OUTPUT_DIR, repo_root, write_json
from .aoi_mcp_registry_recovery_gate import OUTPUT_PATH as GATE_OUTPUT_PATH
from .aoi_mcp_registry_recovery_gate import SERVER_JSON, run_recovery_gate
from .mcp_publisher_installer import find_mcp_publisher


OUTPUT_PATH = OUTPUT_DIR / "AOI_MCP_REGISTRY_RECOVERY_PUBLISH_RESULT.json"
CONFIRM_ENV = "AOI_MCP_REGISTRY_SUBMIT_CONFIRM"


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


def _read_gate() -> dict[str, Any]:
    full = repo_root() / GATE_OUTPUT_PATH
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def run_recovery_publish(
    env: dict[str, str] | None = None,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    publisher_finder: Callable[[], str] = find_mcp_publisher,
    write_result: bool = True,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    gate = _read_gate() or run_recovery_gate(write_result=True)
    publisher = publisher_finder()
    env_confirm_present = env_map.get(CONFIRM_ENV) == "YES"
    logout_result: dict[str, Any] = {"skipped": True}
    login_result: dict[str, Any] = {"skipped": True}
    publish_result: dict[str, Any] = {"skipped": True}
    errors: list[str] = []
    warnings: list[str] = []
    submission_performed = False

    if gate.get("decision") != "PASS_READY_FOR_MCP_REGISTRY_RECOVERY_PUBLISH":
        decision = "HOLD_GATE_NOT_PASS"
        warnings.append(f"Recovery gate is {gate.get('decision')}.")
    elif not env_confirm_present:
        decision = "HOLD_ENV_CONFIRM_REQUIRED"
        warnings.append(f"{CONFIRM_ENV}=YES is required before registry publish.")
    elif not publisher:
        decision = "HOLD_MCP_PUBLISHER_REQUIRED"
        warnings.append("mcp-publisher is not available.")
    else:
        logout_result = runner([publisher, "logout"], 120)
        login_result = runner([publisher, "login", "github"], 300)
        if not login_result.get("ok"):
            decision = "HOLD_LOGIN_REQUIRED"
            warnings.append("mcp-publisher GitHub login did not complete.")
        else:
            publish_result = runner([publisher, "publish", str(SERVER_JSON)], 300)
            combined = f"{publish_result.get('stdout', '')}\n{publish_result.get('stderr', '')}".lower()
            if publish_result.get("ok"):
                decision = "PASS_MCP_REGISTRY_RECOVERY_PUBLISHED"
                submission_performed = True
            elif "already" in combined or "exists" in combined:
                decision = "HOLD_ALREADY_PUBLISHED_OR_VERSION_EXISTS"
                warnings.append("Registry entry or version appears to already exist.")
            else:
                decision = "BLOCK_PUBLISH_FAILED"
                errors.append("mcp-publisher publish failed.")

    result = {
        "schema": "AOI_MCPRegistryRecoveryPublishResult/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "gate_decision": gate.get("decision"),
        "env_confirm_present": env_confirm_present,
        "mcp_publisher_path": publisher,
        "logout_result": logout_result,
        "login_result": login_result,
        "publish_result": publish_result,
        "submission_performed": submission_performed,
        "token_printed": False,
        "upload_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_recovery_publish()
    print(
        "aoi_mcp_registry_recovery_publish: "
        f"{result['decision']} submission_performed={result['submission_performed']}"
    )


if __name__ == "__main__":
    main()
