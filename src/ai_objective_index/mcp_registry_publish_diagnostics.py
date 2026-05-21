from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .mcp_publisher_installer import find_mcp_publisher
from .mcp_registry_failure_classifier import (
    classify_publish_failure,
    redact_sensitive,
    write_failure_classification,
)
from .real_pypi_upload_gate import _repo_root


WAVE_DIR = Path("public_launch") / "wave14_mcp_registry_diagnostics"
VALIDATE_OUTPUT_PATH = WAVE_DIR / "MCP_PUBLISHER_VALIDATE_RESULT.json"
SUMMARY_PATH = WAVE_DIR / "MCP_REGISTRY_DIAGNOSTIC_SUMMARY.md"
RECOVERY_PATH = WAVE_DIR / "MCP_REGISTRY_NEXT_RECOVERY_STEPS.md"
SUBMIT_RESULT_PATH = Path("public_launch") / "wave13_mcp_registry_submit" / "MCP_REGISTRY_SUBMIT_RESULT.json"
SERVER_JSON = ".mcp/server.json"


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _run_publisher_command(command: list[str], timeout: int = 180) -> dict[str, Any]:
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
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": redact_sensitive(exc),
            "command_redacted": " ".join(command),
            "token_printed": False,
        }
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": redact_sensitive(completed.stdout),
        "stderr": redact_sensitive(completed.stderr),
        "command_redacted": " ".join(command),
        "token_printed": False,
    }


def validate_server_json(publisher: str | None = None, write_result: bool = True) -> dict[str, Any]:
    binary = publisher or find_mcp_publisher()
    warnings: list[str] = []
    errors: list[str] = []
    if not binary:
        result = {
            "generated_at": datetime.now(UTC).isoformat(),
            "decision": "HOLD_MCP_PUBLISHER_MISSING",
            "mcp_publisher_path": "",
            "validate_command": "",
            "validate_result": {},
            "validate_ok": False,
            "token_printed": False,
            "errors": ["mcp-publisher is not available."],
            "warnings": warnings,
        }
    else:
        command = [binary, "validate", SERVER_JSON]
        validate_result = _run_publisher_command(command)
        if validate_result.get("ok"):
            decision = "PASS_VALIDATE"
        else:
            decision = "BLOCK_VALIDATE_FAILED"
            errors.append("mcp-publisher validate failed.")
        result = {
            "generated_at": datetime.now(UTC).isoformat(),
            "decision": decision,
            "mcp_publisher_path": binary,
            "validate_command": " ".join(command),
            "validate_result": validate_result,
            "validate_ok": bool(validate_result.get("ok")),
            "token_printed": False,
            "errors": errors,
            "warnings": warnings,
        }
    if write_result:
        _write_json(VALIDATE_OUTPUT_PATH, result)
    return result


def _recovery_steps(classification: str) -> list[str]:
    if classification == "VALIDATE_PASS_NO_PUBLISH":
        return ["No recovery is required for validation.", "Ask for explicit publish confirmation before running submit."]
    if classification == "AUTH_REQUIRED":
        return ["Rerun local GitHub login with tools/mcp-publisher/mcp-publisher.exe login github.", "Rerun diagnostics before publishing."]
    if classification == "NAMESPACE_MISMATCH":
        return ["Check .mcp/server.json name and README mcp-name marker.", "Confirm GitHub repository ownership for the namespace."]
    if classification == "SERVER_JSON_INVALID":
        return ["Fix .mcp/server.json according to validate output.", "Rerun mcp_registry_publish_diagnostics."]
    if classification == "VERSION_ALREADY_EXISTS":
        return ["Do not retry the same version blindly.", "If a fix is required, prepare 0.3.0a2 and publish PyPI first."]
    if classification == "NETWORK_ERROR":
        return ["Retry once after network/proxy is stable.", "Do not change PyPI or bump version for a transient network failure."]
    if classification == "REGISTRY_API_ERROR":
        return ["Wait and retry diagnostics.", "Capture registry status without exposing tokens."]
    if classification == "PUBLISH_SUCCESS":
        return ["Run registry reconcile and discovery report.", "Monitor registry search propagation."]
    return ["Inspect redacted stdout/stderr.", "Rerun login only if output suggests authentication failure."]


def write_diagnostic_summary(
    validate_result: dict[str, Any],
    classification: dict[str, Any] | None = None,
    publish_attempted: bool = False,
) -> None:
    failure = classification or classify_publish_failure(
        stdout=(validate_result.get("validate_result") or {}).get("stdout"),
        stderr=(validate_result.get("validate_result") or {}).get("stderr"),
        returncode=(validate_result.get("validate_result") or {}).get("returncode"),
        validate_ok=validate_result.get("validate_ok"),
    )
    write_failure_classification(failure)
    steps = _recovery_steps(str(failure.get("classification")))
    _write(
        SUMMARY_PATH,
        f"""# MCP Registry Diagnostic Summary

- Validate decision: `{validate_result.get('decision')}`
- Validate ok: `{str(bool(validate_result.get('validate_ok'))).lower()}`
- Publisher path: `{validate_result.get('mcp_publisher_path')}`
- Publish attempted: `{str(publish_attempted).lower()}`
- Failure classification: `{failure.get('classification')}`
- Token printed: false

Registry publication is a metadata listing, not verification, security certification, a quality guarantee, product readiness, purchasing advice, or action authorization.
""",
    )
    _write(
        RECOVERY_PATH,
        "# MCP Registry Next Recovery Steps\n\n" + "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1)) + "\n",
    )


def run_mcp_registry_publish_diagnostics(write_result: bool = True) -> dict[str, Any]:
    validate_result = validate_server_json(write_result=write_result)
    submit_result = _read_json(SUBMIT_RESULT_PATH)
    publish_result = submit_result.get("publish_result") if isinstance(submit_result.get("publish_result"), dict) else {}
    publish_attempted = bool(submit_result.get("execute") and publish_result)
    if publish_attempted:
        classification = classify_publish_failure(
            stdout=publish_result.get("stdout"),
            stderr=publish_result.get("stderr"),
            returncode=publish_result.get("returncode"),
            validate_ok=validate_result.get("validate_ok"),
        )
    elif validate_result.get("validate_ok"):
        classification = {
            "generated_at": datetime.now(UTC).isoformat(),
            "classification": "VALIDATE_PASS_NO_PUBLISH",
            "returncode": (validate_result.get("validate_result") or {}).get("returncode"),
            "validate_ok": True,
            "matched_patterns": ["validate_ok and publish_attempted == false"],
            "token_printed": False,
            "token_like_detected_before_redaction": False,
        }
    else:
        classification = classify_publish_failure(
            stdout=(validate_result.get("validate_result") or {}).get("stdout"),
            stderr=(validate_result.get("validate_result") or {}).get("stderr"),
            returncode=(validate_result.get("validate_result") or {}).get("returncode"),
            validate_ok=validate_result.get("validate_ok"),
        )
    if write_result:
        write_diagnostic_summary(validate_result, classification=classification, publish_attempted=publish_attempted)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "validate": validate_result,
        "latest_submit_result_token": submit_result.get("result_token"),
        "classification": classification,
        "publish_attempted": publish_attempted,
        "token_printed": False,
    }


def main() -> None:
    result = run_mcp_registry_publish_diagnostics()
    validate = result["validate"]
    print(
        "mcp_registry_publish_diagnostics: "
        f"{validate['decision']} validate_ok={validate['validate_ok']}"
    )


if __name__ == "__main__":
    main()
