from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .mcp_registry_server_json_builder import SERVER_JSON_PATH, namespace_is_valid, write_server_json


WAVE1_DIR = Path("public_launch") / "wave1"
ELIGIBILITY_PATH = WAVE1_DIR / "MCP_REGISTRY_ELIGIBILITY_RESULT.json"
SUBMISSION_PATH = WAVE1_DIR / "MCP_REGISTRY_SUBMISSION_RESULT.json"
CONFIRM_ENV = "AOI_MCP_REGISTRY_SUBMIT_CONFIRM"
CONFIRM_VALUE = "YES"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _sanitize(value: Any) -> str:
    text = str(value or "")
    lowered = text.lower()
    for marker in ["gho_", "ghp_", "github_pat_", "hf_", "bearer "]:
        index = lowered.find(marker)
        if index >= 0:
            return text[:index] + "[redacted]"
    return text[:1000]


def _run(command: list[str], timeout: int = 120) -> dict[str, Any]:
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
            "command": command,
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": _sanitize(completed.stdout),
            "stderr": _sanitize(completed.stderr),
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": _sanitize(exc)}


def _read_json(path: str | Path) -> dict[str, Any]:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def evaluate_mcp_registry_eligibility(
    server_json: dict[str, Any] | None = None,
    mcp_publisher_available: bool | None = None,
) -> dict[str, Any]:
    server_json = server_json or write_server_json()
    mcp_publisher_available = shutil.which("mcp-publisher") is not None if mcp_publisher_available is None else mcp_publisher_available
    errors: list[str] = []
    warnings: list[str] = []
    holds: list[str] = []
    decision = "PASS_SUBMIT_READY"

    name = str(server_json.get("name") or "")
    if not namespace_is_valid(name):
        decision = "BLOCK_INVALID_NAMESPACE"
        errors.append("Server name namespace is invalid.")
    elif server_json.get("draft_not_submittable"):
        decision = "HOLD_SERVER_JSON_DRAFT_ONLY"
        holds.append("server.json is a draft because no package artifact or remote MCP endpoint is available.")
    elif not server_json.get("entrypoints", {}).get("stdio_entrypoint_exists"):
        decision = "HOLD_NO_REMOTE_MCP_ENDPOINT"
        holds.append("MCP entrypoint is missing.")
    elif not server_json.get("artifacts", {}).get("python_package_artifact_exists") and not server_json.get("artifacts", {}).get("remote_mcp_endpoint_exists"):
        decision = "HOLD_PACKAGE_NOT_PUBLISHED"
        holds.append("No package artifact or remote MCP endpoint is available.")
    elif not mcp_publisher_available:
        decision = "HOLD_MCP_PUBLISHER_MISSING"
        holds.append("mcp-publisher CLI is unavailable.")

    claim = _read_json("data/generated/launch_claim_guard_result_v0_2.json")
    if claim and claim.get("overall_token") != "PASS":
        decision = "BLOCK_OVERCLAIM"
        errors.append("Launch claim guard is not PASS.")

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "server_json_path": str(SERVER_JSON_PATH),
        "server_name": name,
        "server_json_valid_namespace": namespace_is_valid(name),
        "draft_not_submittable": bool(server_json.get("draft_not_submittable")),
        "mcp_publisher_available": mcp_publisher_available,
        "registry_authentication_available": "not_checked",
        "errors": errors,
        "warnings": warnings,
        "holds": holds,
        "token_printed": False,
        "submission_performed": False,
    }


def run_mcp_registry_submission_gate(
    execute: bool = False,
    env: dict[str, str] | None = None,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
    mcp_publisher_available: bool | None = None,
) -> dict[str, Any]:
    env = env if env is not None else os.environ
    server_json = write_server_json()
    eligibility = evaluate_mcp_registry_eligibility(server_json, mcp_publisher_available=mcp_publisher_available)
    submission = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "eligibility_decision": eligibility["decision"],
        "submission_performed": False,
        "token_printed": False,
        "errors": [],
        "warnings": [],
        "next_action": "",
    }

    if execute:
        if env.get(CONFIRM_ENV) != CONFIRM_VALUE:
            submission["errors"].append(f"Missing explicit confirmation: set {CONFIRM_ENV}={CONFIRM_VALUE}.")
            submission["next_action"] = "No MCP Registry submission performed."
        elif eligibility["decision"] != "PASS_SUBMIT_READY":
            submission["errors"].append(f"Eligibility is not PASS: {eligibility['decision']}.")
            submission["next_action"] = "Resolve HOLD/BLOCK conditions before submitting."
        else:
            result = runner(["mcp-publisher", "publish", str(SERVER_JSON_PATH)], 180)
            if result.get("ok"):
                submission["submission_performed"] = True
                submission["next_action"] = "MCP Registry submission command completed; verify registry page manually."
            else:
                submission["errors"].append(result.get("stderr") or result.get("stdout") or "mcp-publisher failed")
                submission["next_action"] = "Review mcp-publisher error. Do not retry blindly."
    else:
        submission["next_action"] = "Dry-run only. Submission requires PASS eligibility and explicit environment confirmation."

    if write_result:
        _write_json(ELIGIBILITY_PATH, eligibility)
        _write_json(SUBMISSION_PATH, submission)
    return {"eligibility": eligibility, "submission": submission}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="MCP Registry submission eligibility gate.")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    result = run_mcp_registry_submission_gate(execute=bool(args.execute) and not bool(args.dry_run))
    print(
        "mcp_registry_submission_gate: "
        f"decision={result['eligibility']['decision']} "
        f"submission_performed={result['submission']['submission_performed']}"
    )


if __name__ == "__main__":
    main()
