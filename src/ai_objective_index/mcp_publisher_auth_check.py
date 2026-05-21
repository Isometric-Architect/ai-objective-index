from __future__ import annotations

import json
import subprocess
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .mcp_publisher_installer import find_mcp_publisher, redact_token_like
from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "wave13_mcp_registry_submit" / "MCP_PUBLISHER_AUTH_RESULT.json"
SERVER_JSON = ".mcp/server.json"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _run_login(command: str) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [command, "login", "github"],
            cwd=_repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=900,
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


def _run_non_publishing_probe(command: str) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for args in ([command, "validate", SERVER_JSON], [command, "publish", "--help"]):
        try:
            completed = subprocess.run(
                args,
                cwd=_repo_root(),
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=60,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
            checks.append(
                {
                    "command_redacted": " ".join(args),
                    "ok": False,
                    "returncode": None,
                    "stdout": "",
                    "stderr": redact_token_like(exc),
                }
            )
            continue
        checks.append(
            {
                "command_redacted": " ".join(args),
                "ok": completed.returncode == 0,
                "returncode": completed.returncode,
                "stdout": redact_token_like(completed.stdout),
                "stderr": redact_token_like(completed.stderr),
            }
        )
        if completed.returncode == 0:
            break
    return {
        "ok": any(check.get("ok") for check in checks),
        "checks": checks,
        "publish_or_validate_can_run": any(check.get("ok") for check in checks),
        "auth_status_command_available": False,
    }


def run_mcp_publisher_auth_check(mode: str = "check", write_result: bool = True) -> dict[str, Any]:
    command = find_mcp_publisher()
    warnings: list[str] = []
    errors: list[str] = []
    login_result: dict[str, Any] = {}
    non_publishing_probe: dict[str, Any] = {}
    login_attempted = False
    auth_available = False

    if not command:
        decision = "HOLD_LOGIN_REQUIRED"
        warnings.append("mcp-publisher is not available, so auth status cannot be checked.")
    elif mode == "login":
        login_attempted = True
        login_result = _run_login(command)
        if login_result.get("ok"):
            decision = "PASS_AUTH_CONFIRMED"
            auth_available = True
        else:
            decision = "BLOCK_LOGIN_FAILED"
            errors.append("mcp-publisher login github did not complete successfully.")
    else:
        non_publishing_probe = _run_non_publishing_probe(command)
        if non_publishing_probe.get("publish_or_validate_can_run"):
            decision = "PASS_AUTH_ASSUMED_FROM_DIRECT_LOGIN"
            auth_available = True
            warnings.append(
                "mcp-publisher has no reliable auth status check; treating prior direct login as available because a non-publishing publisher probe ran."
            )
        else:
            decision = "HOLD_AUTH_STATUS_NOT_CHECKED"
            warnings.append("No reliable mcp-publisher auth status command is assumed; run --login before submit.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "decision": decision,
        "mcp_publisher_available": bool(command),
        "mcp_publisher_path": command,
        "auth_available": auth_available,
        "login_attempted": login_attempted,
        "login_result": login_result,
        "non_publishing_probe": non_publishing_probe,
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
    group.add_argument("--check", action="store_true")
    group.add_argument("--login", action="store_true")
    args = parser.parse_args()
    mode = "login" if args.login else "check"
    result = run_mcp_publisher_auth_check(mode=mode)
    print(f"mcp_publisher_auth_check: {result['decision']} login_attempted={result['login_attempted']}")


if __name__ == "__main__":
    main()
