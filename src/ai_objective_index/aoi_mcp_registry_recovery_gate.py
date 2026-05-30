from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .aoi_030a2_build_verify import sanitize
from .aoi_030a2_marker_sync import (
    CANONICAL_MCP_NAME,
    MCP_MARKER,
    OUTPUT_DIR,
    PACKAGE_NAME,
    TARGET_VERSION,
    current_marker_state,
    repo_root,
    read_json,
    read_text,
    run_marker_sync,
    write_json,
)
from .aoi_030a2_pypi_upload_gate import tracked_token_findings
from .aoi_030a2_pypi_verify import OUTPUT_PATH as PYPI_VERIFY_OUTPUT_PATH
from .mcp_publisher_installer import find_mcp_publisher


OUTPUT_PATH = OUTPUT_DIR / "AOI_MCP_REGISTRY_RECOVERY_GATE_RESULT.json"
SERVER_JSON = Path(".mcp") / "server.json"


def _run(command: list[str], timeout: int = 120) -> dict[str, Any]:
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


def _claim_guard_passed() -> bool:
    payload = read_json(Path("data") / "generated" / "launch_claim_guard_result_v0_2.json")
    return not payload or payload.get("overall_token") == "PASS" or int(payload.get("risky_phrase_count", 0) or 0) == 0


def _tech_protection_passed() -> bool:
    payload = read_json(Path("public_launch") / "ROE_TECHNICAL_PROTECTION_GATE_RESULT.json")
    if not payload:
        payload = read_json(Path("data") / "generated" / "tech_protection_audit_result.json")
    decision = str(payload.get("decision") or payload.get("overall_token") or "")
    return not payload or decision in {"PASS_NO_SENSITIVE_KERNEL_EXPOSED", "PASS"}


def _validate_server_json(binary: str, runner: Callable[[list[str], int], dict[str, Any]]) -> dict[str, Any]:
    if not binary:
        return {"ok": False, "skipped": True, "reason": "mcp-publisher not found"}
    return runner([binary, "validate", str(SERVER_JSON)], 120)


def run_recovery_gate(
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    publisher_finder: Callable[[], str] = find_mcp_publisher,
    token_scanner: Callable[[], list[str]] = tracked_token_findings,
    write_result: bool = True,
) -> dict[str, Any]:
    marker = run_marker_sync(write_result=True)
    state = current_marker_state()
    verify = read_json(PYPI_VERIFY_OUTPUT_PATH)
    publisher = publisher_finder()
    validate = _validate_server_json(publisher, runner)
    token_findings = token_scanner()
    readme = read_text(Path("README.md"))
    errors: list[str] = []
    warnings: list[str] = []

    metadata_ok = (
        state.get("server_name") == CANONICAL_MCP_NAME
        and state.get("server_version") == TARGET_VERSION
        and state.get("server_package_registry_type") == "pypi"
        and state.get("server_package_identifier") == PACKAGE_NAME
        and state.get("server_package_version") == TARGET_VERSION
        and MCP_MARKER in readme
    )
    if token_findings:
        decision = "BLOCK_SECRET_FINDING"
        errors.append("Tracked token-like content found.")
    elif not _claim_guard_passed():
        decision = "BLOCK_OVERCLAIM"
        errors.append("Launch claim guard is not PASS.")
    elif not _tech_protection_passed():
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
        errors.append("Tech protection audit is not PASS.")
    elif marker.get("decision") != "PASS_MARKER_SYNCED_030A2" or not metadata_ok:
        decision = "BLOCK_METADATA_MISMATCH"
        errors.append("README/server.json/PyPI package metadata are not synchronized.")
    elif verify.get("decision") != "PASS_PYPI_030A2_VERIFIED":
        decision = "HOLD_PYPI_VERIFY_REQUIRED"
        warnings.append("PyPI 0.3.0a2 install verification has not passed.")
    elif not publisher:
        decision = "HOLD_MCP_PUBLISHER_REQUIRED"
        warnings.append("mcp-publisher is not available.")
    elif not validate.get("ok"):
        decision = "BLOCK_SERVER_JSON_INVALID"
        errors.append("mcp-publisher validate did not pass.")
    else:
        decision = "PASS_READY_FOR_MCP_REGISTRY_RECOVERY_PUBLISH"

    result = {
        "schema": "AOI_MCPRegistryRecoveryGateResult/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "server_name": state.get("server_name"),
        "server_version": state.get("server_version"),
        "registry_type": state.get("server_package_registry_type"),
        "identifier": state.get("server_package_identifier"),
        "package_version": state.get("server_package_version"),
        "readme_marker_matches": MCP_MARKER in readme,
        "pypi_verify_decision": verify.get("decision"),
        "mcp_publisher_path": publisher,
        "mcp_publisher_validate": validate,
        "token_like_tracked_findings": token_findings,
        "token_printed": False,
        "upload_performed": False,
        "mcp_registry_submission_performed": False,
        "can_claim_certification": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_recovery_gate()
    print(f"aoi_mcp_registry_recovery_gate: {result['decision']} submission_performed=False")


if __name__ == "__main__":
    main()
