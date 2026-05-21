from __future__ import annotations

import json
import os
import shutil
import subprocess
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .mcp_registry_manifest_final_audit import run_mcp_registry_manifest_final_audit
from .mcp_publisher_setup import run_mcp_publisher_setup
from .real_pypi_upload_gate import _repo_root


DRY_RUN_OUTPUT_PATH = Path("public_launch") / "wave11_mcp_registry" / "MCP_REGISTRY_PUBLISH_DRY_RUN_RESULT.json"
OUTPUT_PATH = Path("public_launch") / "wave11_mcp_registry" / "MCP_REGISTRY_PUBLISH_RESULT.json"
CONFIRM_ENV = "AOI_MCP_REGISTRY_SUBMIT_CONFIRM"
PUBLISH_COMMAND = ["mcp-publisher", "publish", ".mcp/server.json"]
LOGIN_COMMAND = ["mcp-publisher", "login", "github"]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def redact_token_like(text: Any) -> str:
    value = str(text or "")
    prefixes = ["ghp_", "gho_", "ghu_", "ghs_", "github_pat_", "pypi-", "hf_", "Bearer "]
    for prefix in prefixes:
        value = value.replace(prefix, f"{prefix}[redacted]")
    return value[:4000]


def _run_command(command: list[str], timeout: int = 240) -> dict[str, Any]:
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
        return {"returncode": None, "stdout": "", "stderr": redact_token_like(exc), "ok": False}
    return {
        "returncode": completed.returncode,
        "stdout": redact_token_like(completed.stdout),
        "stderr": redact_token_like(completed.stderr),
        "ok": completed.returncode == 0,
    }


def _base_result(mode: str) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "dry_run": mode == "dry-run",
        "login": mode == "login",
        "execute": mode == "execute",
        "submission_performed": False,
        "command_redacted": " ".join(PUBLISH_COMMAND),
        "login_command_redacted": " ".join(LOGIN_COMMAND),
        "token_printed": False,
        "errors": [],
        "warnings": [],
    }


def run_mcp_registry_publish_runner(
    mode: str = "dry-run",
    env: dict[str, str] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    result = _base_result(mode)
    setup = run_mcp_publisher_setup(write_result=False)
    manifest = run_mcp_registry_manifest_final_audit(write_result=False)
    publisher_path = shutil.which("mcp-publisher")
    result["mcp_publisher_setup_decision"] = setup.get("decision")
    result["manifest_audit_decision"] = manifest.get("decision")
    result["mcp_publisher_available"] = bool(publisher_path)
    result["env_confirm_present"] = env_map.get(CONFIRM_ENV) == "YES"

    if mode == "dry-run":
        if manifest.get("decision") != "PASS_MANIFEST_READY":
            result["result_token"] = "BLOCK_MANIFEST_NOT_READY"
            result["errors"].append("Manifest final audit is not PASS.")
        elif not publisher_path:
            result["result_token"] = "HOLD_LOGIN_REQUIRED"
            result["warnings"].append("mcp-publisher is missing; install and login before execute.")
        else:
            result["result_token"] = "DRY_RUN_ONLY"
            result["warnings"].append("Dry-run only; no registry submission performed.")
        if write_result:
            _write_json(DRY_RUN_OUTPUT_PATH, result)
            publish_result = dict(result)
            publish_result["dry_run"] = True
            publish_result["execute"] = False
            publish_result["submission_performed"] = False
            _write_json(OUTPUT_PATH, publish_result)
        return result

    if mode == "login":
        if not publisher_path:
            result["result_token"] = "HOLD_LOGIN_REQUIRED"
            result["warnings"].append("mcp-publisher is missing; login was not attempted.")
        else:
            command_result = _run_command(LOGIN_COMMAND, timeout=600)
            result["login_attempted"] = True
            result["login_result"] = command_result
            result["result_token"] = "LOGIN_SUCCESS" if command_result.get("ok") else "HOLD_LOGIN_REQUIRED"
            if not command_result.get("ok"):
                result["warnings"].append("mcp-publisher login did not complete successfully.")
        if write_result:
            _write_json(OUTPUT_PATH, result)
        return result

    if mode == "execute":
        if manifest.get("decision") != "PASS_MANIFEST_READY":
            result["result_token"] = "BLOCK_MANIFEST_NOT_READY"
            result["errors"].append("Manifest final audit is not PASS.")
        elif not publisher_path:
            result["result_token"] = "HOLD_LOGIN_REQUIRED"
            result["warnings"].append("mcp-publisher is missing or not authenticated.")
        elif env_map.get(CONFIRM_ENV) != "YES":
            result["result_token"] = "HOLD_ENV_CONFIRM_REQUIRED"
            result["warnings"].append(f"{CONFIRM_ENV}=YES is required before registry submission.")
        else:
            command_result = _run_command(PUBLISH_COMMAND, timeout=300)
            result["publish_result"] = command_result
            combined = f"{command_result.get('stdout', '')}\n{command_result.get('stderr', '')}".lower()
            if command_result.get("ok"):
                result["result_token"] = "PUBLISH_SUCCESS"
                result["submission_performed"] = True
            elif "already" in combined or "exists" in combined:
                result["result_token"] = "HOLD_ALREADY_PUBLISHED_OR_VERSION_EXISTS"
                result["warnings"].append("Registry publish appears to have already happened or this version exists.")
            else:
                result["result_token"] = "BLOCK_PUBLISH_FAILED"
                result["errors"].append("mcp-publisher publish failed.")
        if write_result:
            _write_json(OUTPUT_PATH, result)
        return result

    raise ValueError(f"unsupported mode: {mode}")


def main() -> None:
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--login", action="store_true")
    group.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    mode = "dry-run"
    if args.login:
        mode = "login"
    elif args.execute:
        mode = "execute"
    result = run_mcp_registry_publish_runner(mode=mode)
    print(
        "mcp_registry_publish_runner: "
        f"{result['result_token']} "
        f"submission_performed={result['submission_performed']}"
    )


if __name__ == "__main__":
    main()
