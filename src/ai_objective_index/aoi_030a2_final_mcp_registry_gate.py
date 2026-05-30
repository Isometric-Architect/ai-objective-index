from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

from .aoi_030a2_build_verify import sanitize
from .aoi_030a2_final_common import (
    CANONICAL_MCP_NAME,
    CONFIRM_MCP_ENV,
    FINAL_MCP_GATE_PATH,
    FINAL_PREFLIGHT_PATH,
    FINAL_PYPI_VERIFY_PATH,
    MCP_MARKER,
    PACKAGE_NAME,
    TARGET_VERSION,
    now,
    read_json,
    read_text,
    repo_root,
    write_json,
)
from .aoi_030a2_final_preflight import run_final_preflight
from .aoi_030a2_marker_sync import current_marker_state
from .aoi_030a2_pypi_upload_gate import tracked_token_findings
from .mcp_publisher_installer import find_mcp_publisher


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


def _read_or_run_preflight() -> dict[str, Any]:
    payload = read_json(FINAL_PREFLIGHT_PATH)
    if payload:
        return payload
    return run_final_preflight(write_result=True)


def run_final_mcp_registry_gate(
    env: dict[str, str] | None = None,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    publisher_finder: Callable[[], str] = find_mcp_publisher,
    token_scanner: Callable[[], list[str]] = tracked_token_findings,
    pypi_verify_result: dict[str, Any] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    verify = pypi_verify_result if pypi_verify_result is not None else read_json(FINAL_PYPI_VERIFY_PATH)
    preflight = _read_or_run_preflight()
    state = current_marker_state()
    server = read_json(SERVER_JSON)
    readme = read_text(Path("README.md"))
    publisher = publisher_finder()
    validate = {"skipped": True, "ok": False}
    token_findings = token_scanner()
    env_confirm_present = env_map.get(CONFIRM_MCP_ENV) == "YES"
    errors: list[str] = []
    warnings: list[str] = []

    metadata_ok = (
        server.get("name") == CANONICAL_MCP_NAME
        and server.get("version") == TARGET_VERSION
        and state.get("server_package_registry_type") == "pypi"
        and state.get("server_package_identifier") == PACKAGE_NAME
        and state.get("server_package_version") == TARGET_VERSION
        and MCP_MARKER in readme
    )
    if verify.get("decision") == "PASS_REAL_PYPI_INSTALL_030A2" and publisher:
        validate = runner([publisher, "validate", str(SERVER_JSON)], 120)

    if token_findings:
        decision = "BLOCK_SECRET_FINDING"
        errors.append("Tracked token-like content found.")
    elif preflight.get("decision") != "PASS_READY_FOR_FINAL_PYPI_UPLOAD":
        decision = "HOLD_FINAL_PREFLIGHT_REQUIRED"
        warnings.append(f"Final preflight is {preflight.get('decision')}.")
    elif verify.get("decision") != "PASS_REAL_PYPI_INSTALL_030A2":
        decision = "HOLD_PYPI_VERIFY_REQUIRED"
        warnings.append(f"PyPI verify is {verify.get('decision')}.")
    elif not metadata_ok:
        decision = "BLOCK_METADATA_MISMATCH"
        errors.append("server.json, README marker, or package metadata does not match 0.3.0a2.")
    elif not publisher:
        decision = "HOLD_MCP_PUBLISHER_REQUIRED"
        warnings.append("mcp-publisher is not available.")
    elif not validate.get("ok"):
        decision = "BLOCK_SERVER_JSON_INVALID"
        errors.append("mcp-publisher validate did not pass.")
    elif not env_confirm_present:
        decision = "PASS_READY_FOR_MCP_REGISTRY_PUBLISH_ENV_REQUIRED"
        warnings.append(f"{CONFIRM_MCP_ENV}=YES is required before registry publish.")
    else:
        decision = "PASS_READY_FOR_MCP_REGISTRY_PUBLISH"

    result = {
        "schema": "AOI_030A2FinalMCPRegistryGateResult/v0.1",
        "generated_at": now(),
        "decision": decision,
        "server_name": server.get("name"),
        "server_version": server.get("version"),
        "registry_type": state.get("server_package_registry_type"),
        "identifier": state.get("server_package_identifier"),
        "package_version": state.get("server_package_version"),
        "readme_marker_matches": MCP_MARKER in readme,
        "pypi_verify_decision": verify.get("decision"),
        "preflight_decision": preflight.get("decision"),
        "mcp_publisher_path": publisher,
        "mcp_publisher_validate": validate,
        "env_confirm_present": env_confirm_present,
        "token_like_tracked_findings": token_findings,
        "token_printed": False,
        "upload_performed": False,
        "mcp_registry_publish_performed": False,
        "can_claim_certification": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(FINAL_MCP_GATE_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_final_mcp_registry_gate()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"aoi_030a2_final_mcp_registry_gate: {result['decision']} submission_performed=False")


if __name__ == "__main__":
    main()

