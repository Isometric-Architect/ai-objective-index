from __future__ import annotations

import argparse
import json
import os
from typing import Any, Callable

from .aoi_030a2_final_common import (
    CONFIRM_PYPI_ENV,
    FINAL_BUILD_PATH,
    FINAL_PREFLIGHT_PATH,
    FINAL_PYPI_UPLOAD_GATE_PATH,
    PACKAGE_NAME,
    SDIST_PATH,
    TARGET_VERSION,
    WHEEL_PATH,
    dist_paths_exist,
    now,
    pypirc_exists,
    read_json,
    token_file_candidates,
    write_json,
)
from .aoi_030a2_final_preflight import run_final_preflight
from .aoi_030a2_pypi_upload_gate import _pypi_status, tracked_token_findings


def _read_or_run_preflight() -> dict[str, Any]:
    payload = read_json(FINAL_PREFLIGHT_PATH)
    if payload:
        return payload
    return run_final_preflight(write_result=True)


def run_final_pypi_upload_gate(
    env: dict[str, str] | None = None,
    pypi_checker: Callable[[], dict[str, Any]] = _pypi_status,
    token_scanner: Callable[[], list[str]] = tracked_token_findings,
    preflight_result: dict[str, Any] | None = None,
    build_result: dict[str, Any] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    preflight = preflight_result if preflight_result is not None else _read_or_run_preflight()
    build = build_result if build_result is not None else read_json(FINAL_BUILD_PATH)
    pypi = pypi_checker()
    token_findings = token_scanner()
    token_candidates = token_file_candidates()
    env_confirm_present = env_map.get(CONFIRM_PYPI_ENV) == "YES"
    exists = dist_paths_exist()
    errors: list[str] = []
    warnings: list[str] = []

    if preflight.get("decision") != "PASS_READY_FOR_FINAL_PYPI_UPLOAD":
        warnings.append(f"Final preflight is {preflight.get('decision')}.")
    if build.get("decision") != "PASS_FINAL_BUILD_READY":
        warnings.append(f"Final build is {build.get('decision')}.")
    if not exists["wheel_exists"] or not exists["sdist_exists"]:
        warnings.append("0.3.0a2 wheel or sdist is missing.")
    if not pypi.get("checked"):
        warnings.append("PyPI version availability could not be checked.")
    if pypi.get("status") == "HOLD_VERSION_ALREADY_EXISTS":
        warnings.append("PyPI already reports 0.3.0a2; upload must not overwrite artifacts.")
    if pypirc_exists() or token_findings or token_candidates:
        errors.append("Token file, .pypirc, or token-like tracked content found.")

    if errors:
        decision = "BLOCK_SECRET_FINDING"
    elif pypi.get("status") == "HOLD_VERSION_ALREADY_EXISTS":
        decision = "HOLD_VERSION_ALREADY_EXISTS"
    elif preflight.get("decision") != "PASS_READY_FOR_FINAL_PYPI_UPLOAD" or build.get("decision") != "PASS_FINAL_BUILD_READY":
        decision = "HOLD_FINAL_PREFLIGHT_OR_BUILD_REQUIRED"
    elif not exists["wheel_exists"] or not exists["sdist_exists"]:
        decision = "HOLD_DIST_ARTIFACTS_REQUIRED"
    elif not pypi.get("checked"):
        decision = "HOLD_PYPI_STATUS_NOT_CHECKED"
    elif not env_confirm_present:
        decision = "HOLD_ENV_CONFIRM_REQUIRED"
        warnings.append(f"{CONFIRM_PYPI_ENV}=YES is required before interactive twine upload.")
    else:
        decision = "PASS_READY_FOR_INTERACTIVE_TWINE_UPLOAD"

    result = {
        "schema": "AOI_030A2FinalPyPIUploadGateResult/v0.1",
        "generated_at": now(),
        "decision": decision,
        "target_version": TARGET_VERSION,
        "package_name": PACKAGE_NAME,
        "wheel_path": str(WHEEL_PATH).replace("\\", "/"),
        "sdist_path": str(SDIST_PATH).replace("\\", "/"),
        **exists,
        "preflight_decision": preflight.get("decision"),
        "final_build_decision": build.get("decision"),
        "pypi_status": pypi,
        "env_confirm_present": env_confirm_present,
        "pypirc_exists": pypirc_exists(),
        "token_like_tracked_findings": token_findings,
        "token_file_candidates": token_candidates,
        "upload_performed": False,
        "token_printed": False,
        "mcp_registry_publish_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(FINAL_PYPI_UPLOAD_GATE_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_final_pypi_upload_gate()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"aoi_030a2_final_pypi_upload_gate: {result['decision']} upload_performed=False")


if __name__ == "__main__":
    main()

