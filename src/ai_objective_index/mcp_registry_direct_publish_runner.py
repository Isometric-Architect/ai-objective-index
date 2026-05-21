from __future__ import annotations

import json
import os
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .mcp_publisher_auth_check import OUTPUT_PATH as AUTH_PATH, run_mcp_publisher_auth_check
from .mcp_publisher_installer import find_mcp_publisher
from .mcp_registry_failure_classifier import classify_publish_failure, write_failure_classification
from .mcp_registry_publish_diagnostics import (
    SERVER_JSON,
    WAVE_DIR,
    _run_publisher_command,
    _write,
    _write_json,
    validate_server_json,
    write_diagnostic_summary,
)
from .mcp_registry_publish_preflight import run_mcp_registry_publish_preflight
from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = WAVE_DIR / "MCP_REGISTRY_DIRECT_PUBLISH_RESULT.json"
CONFIRM_ENV = "AOI_MCP_REGISTRY_SUBMIT_CONFIRM"


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _auth_status_allows_override(auth: dict[str, Any], validate: dict[str, Any], env_confirm: bool) -> bool:
    return (
        env_confirm
        and bool(validate.get("validate_ok"))
        and auth.get("decision") in {"HOLD_AUTH_STATUS_NOT_CHECKED", "PASS_AUTH_ASSUMED_FROM_DIRECT_LOGIN", "PASS_AUTH_CONFIRMED"}
    )


def _preflight_allows_publish(preflight: dict[str, Any], auth: dict[str, Any], validate: dict[str, Any], env_confirm: bool) -> tuple[bool, str]:
    decision = str(preflight.get("decision") or "")
    if decision == "PASS_READY_TO_SUBMIT":
        return True, "preflight_pass"
    if decision == "HOLD_AUTH_STATUS_NOT_CHECKED" and _auth_status_allows_override(auth, validate, env_confirm):
        return True, "auth_status_unknown_override_with_validate_and_env_confirm"
    return False, "preflight_not_ready"


def run_mcp_registry_direct_publish(
    execute: bool = False,
    env: dict[str, str] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    env_confirm = env_map.get(CONFIRM_ENV) == "YES"
    publisher = find_mcp_publisher()
    validate = validate_server_json(publisher=publisher or None, write_result=write_result)
    auth = _read_json(AUTH_PATH) or run_mcp_publisher_auth_check(write_result=False)
    preflight = run_mcp_registry_publish_preflight(write_result=True)
    publish_result: dict[str, Any] = {}
    errors: list[str] = []
    warnings: list[str] = []
    submission_performed = False
    publish_attempted = False
    allow_publish, allow_reason = _preflight_allows_publish(preflight, auth, validate, env_confirm)
    command = [publisher or "mcp-publisher", "publish", SERVER_JSON]

    if not execute:
        result_token = "DRY_RUN_ONLY"
        warnings.append("Dry-run only; direct publish was not attempted.")
    elif not env_confirm:
        result_token = "HOLD_ENV_CONFIRM_REQUIRED"
        warnings.append(f"{CONFIRM_ENV}=YES is required before direct publish.")
    elif not publisher:
        result_token = "HOLD_MCP_PUBLISHER_MISSING"
        errors.append("mcp-publisher is not available.")
    elif not validate.get("validate_ok"):
        result_token = "BLOCK_VALIDATE_FAILED"
        errors.append("mcp-publisher validate did not pass; publish refused.")
    elif not allow_publish:
        result_token = "BLOCK_PREFLIGHT_FAILED"
        errors.append(f"Preflight is {preflight.get('decision')}; publish refused.")
    else:
        publish_attempted = True
        publish_result = _run_publisher_command(command, timeout=300)
        if publish_result.get("ok"):
            result_token = "PUBLISH_SUCCESS"
            submission_performed = True
        else:
            result_token = "BLOCK_PUBLISH_FAILED"
            errors.append("mcp-publisher publish failed.")

    classification = classify_publish_failure(
        stdout=publish_result.get("stdout") or (validate.get("validate_result") or {}).get("stdout"),
        stderr=publish_result.get("stderr") or (validate.get("validate_result") or {}).get("stderr"),
        returncode=publish_result.get("returncode") if publish_attempted else (validate.get("validate_result") or {}).get("returncode"),
        validate_ok=validate.get("validate_ok"),
    )
    if not publish_attempted and validate.get("validate_ok") and result_token != "PUBLISH_SUCCESS":
        classification["classification"] = result_token
        classification["matched_patterns"] = ["publish_not_attempted"]

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dry_run": not execute,
        "execute": execute,
        "env_confirm_present": env_confirm,
        "mcp_publisher_path": publisher,
        "validate_decision": validate.get("decision"),
        "validate_ok": bool(validate.get("validate_ok")),
        "preflight_decision": preflight.get("decision"),
        "auth_decision": auth.get("decision"),
        "auth_override_reason": allow_reason,
        "command_redacted": " ".join(command),
        "publish_attempted": publish_attempted,
        "submission_performed": submission_performed,
        "publish_result": publish_result,
        "result_token": result_token,
        "failure_classification": classification.get("classification"),
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
        write_failure_classification(classification)
        write_diagnostic_summary(validate, classification=classification, publish_attempted=publish_attempted)
        _write(
            WAVE_DIR / "MCP_REGISTRY_NEXT_RECOVERY_STEPS.md",
            _recovery_markdown(str(classification.get("classification")), result_token),
        )
    return result


def _recovery_markdown(classification: str, result_token: str) -> str:
    lines = [
        "# MCP Registry Next Recovery Steps",
        "",
        f"- Result token: `{result_token}`",
        f"- Failure classification: `{classification}`",
        "",
    ]
    if classification == "AUTH_REQUIRED":
        lines += [
            "1. Rerun `tools/mcp-publisher/mcp-publisher.exe login github` locally.",
            "2. Rerun diagnostics before another publish attempt.",
        ]
    elif classification == "SERVER_JSON_INVALID":
        lines += ["1. Fix `.mcp/server.json` from validation output.", "2. Rerun diagnostics; do not publish until validation passes."]
    elif classification == "VERSION_ALREADY_EXISTS":
        lines += ["1. Do not retry the same files blindly.", "2. Prepare `0.3.0a2` only if a new version is genuinely needed."]
    elif classification == "NETWORK_ERROR":
        lines += ["1. Retry after network/proxy stability is confirmed.", "2. Do not bump PyPI version for a transient network error."]
    elif classification == "PUBLISH_SUCCESS":
        lines += ["1. Run registry reconcile and discovery report.", "2. Monitor search visibility."]
    else:
        lines += ["1. Review redacted publish stdout/stderr.", "2. Retry only after the specific failure is understood."]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    result = run_mcp_registry_direct_publish(execute=args.execute)
    print(
        "mcp_registry_direct_publish_runner: "
        f"{result['result_token']} classification={result['failure_classification']} "
        f"submission_performed={result['submission_performed']}"
    )


if __name__ == "__main__":
    main()
