from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path
from typing import Any, Callable

import ai_objective_index

from .agent_adoption.capability_card import CAPABILITY_CARD_PATH
from .agent_adoption.package_data_audit import run_package_data_audit
from .agent_adoption.agent_surface_audit import run_agent_surface_audit
from .aoi_030a2_final_common import (
    CANONICAL_MCP_NAME,
    FINAL_PREFLIGHT_PATH,
    MCP_MARKER,
    PACKAGE_NAME,
    TARGET_VERSION,
    committed_mcp_publisher_binaries,
    committed_release_dist_files,
    now,
    pypirc_exists,
    read_json,
    read_text,
    repo_root,
    token_file_candidates,
    write_final_build_result,
    write_json,
)
from .aoi_030a2_marker_sync import current_marker_state, run_marker_sync
from .launch_claim_guard import run_launch_claim_guard
from .no_secrets_audit import run_no_secrets_audit
from .residualops_public_private_alignment_audit import run_public_private_alignment_audit
from .tech_protection_audit import run_tech_protection_audit


OPENAPI_PATH = Path("api") / "openapi.json"
MCP_MANIFEST_PATH = Path("data") / "generated_mcp_tools_manifest.json"
REST_PATHS = [
    "/v1/agents/capability-card",
    "/v1/agents/discover",
    "/v1/agents/preflight",
    "/v1/agents/adoption/status",
]
MCP_TOOLS = [
    "get_aoi_capability_card",
    "discover_capabilities_for_objective",
    "preflight_capability_for_use",
    "explain_aoi_agent_use",
    "list_aoi_agent_examples",
]


def _pyproject_version() -> str:
    path = repo_root() / "pyproject.toml"
    if not path.exists():
        return ""
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return ""
    project = payload.get("project", {}) if isinstance(payload.get("project"), dict) else {}
    return str(project.get("version") or "")


def _server_package(server: dict[str, Any]) -> dict[str, Any]:
    packages = server.get("packages", [])
    if isinstance(packages, list) and packages and isinstance(packages[0], dict):
        return packages[0]
    return {}


def _openapi_agent_paths() -> tuple[list[str], bool]:
    payload = read_json(OPENAPI_PATH)
    paths = payload.get("paths", {}) if isinstance(payload.get("paths"), dict) else {}
    missing = [path for path in REST_PATHS if path not in paths]
    return missing, bool(payload)


def _mcp_agent_tools() -> tuple[list[str], bool]:
    payload = read_json(MCP_MANIFEST_PATH)
    tools = payload.get("tools", []) if isinstance(payload.get("tools"), list) else []
    names = {str(tool.get("name")) for tool in tools if isinstance(tool, dict)}
    missing = [tool for tool in MCP_TOOLS if tool not in names]
    return missing, bool(payload)


def run_final_preflight(
    package_data_runner: Callable[..., dict[str, Any]] = run_package_data_audit,
    surface_runner: Callable[..., dict[str, Any]] = run_agent_surface_audit,
    no_secrets_runner: Callable[[], dict[str, Any]] = run_no_secrets_audit,
    claim_runner: Callable[[], dict[str, Any]] = run_launch_claim_guard,
    tech_runner: Callable[..., dict[str, Any]] = run_tech_protection_audit,
    alignment_runner: Callable[..., dict[str, Any]] = run_public_private_alignment_audit,
    write_result: bool = True,
) -> dict[str, Any]:
    marker = run_marker_sync(write_result=True)
    state = current_marker_state()
    server = read_json(Path(".mcp") / "server.json")
    package = _server_package(server)
    readme = read_text(Path("README.md"))
    card = read_json(CAPABILITY_CARD_PATH)
    package_data = package_data_runner(write_result=True)
    surface = surface_runner(write_result=True)
    build = write_final_build_result()
    no_secrets = no_secrets_runner()
    claim = claim_runner()
    tech = tech_runner(write_result=True)
    alignment = alignment_runner(write_result=True)
    missing_rest, openapi_present = _openapi_agent_paths()
    missing_mcp, mcp_manifest_present = _mcp_agent_tools()
    tracked_dist = committed_release_dist_files()
    tracked_publishers = committed_mcp_publisher_binaries()
    token_candidates = token_file_candidates()

    checks = {
        "pyproject_version": _pyproject_version() == TARGET_VERSION,
        "package_version": ai_objective_index.__version__ == TARGET_VERSION,
        "server_version": server.get("version") == TARGET_VERSION,
        "server_package_version": package.get("version") == TARGET_VERSION,
        "server_package_registry_type": package.get("registryType") == "pypi",
        "server_package_identifier": package.get("identifier") == PACKAGE_NAME,
        "readme_marker": MCP_MARKER in readme,
        "canonical_server_name": server.get("name") == CANONICAL_MCP_NAME,
        "capability_card_version": card.get("version") == TARGET_VERSION,
        "openapi_agent_paths_present": openapi_present and not missing_rest,
        "mcp_agent_tools_present": mcp_manifest_present and not missing_mcp,
        "package_data_audit_pass": package_data.get("decision") == "PASS_AGENT_PACKAGE_DATA_READY",
        "agent_surface_audit_pass": surface.get("decision") == "PASS_AGENT_SURFACES_READY_FOR_030A2_UPLOAD",
        "no_real_secret_findings": int(no_secrets.get("finding_count", 0) or 0) == 0,
        "claim_guard_pass": claim.get("overall_token") == "PASS" and int(claim.get("risky_phrase_count", 0) or 0) == 0,
        "tech_protection_pass": tech.get("decision") in {"PASS_NO_SENSITIVE_KERNEL_EXPOSED", "PASS"},
        "public_private_alignment_pass": alignment.get("decision") == "PASS_PUBLIC_PRIVATE_ALIGNMENT",
        "dist_files_not_committed": not tracked_dist,
        "pypirc_absent": not pypirc_exists(),
        "mcp_publisher_binary_not_committed": not tracked_publishers,
        "token_file_candidates_absent": not token_candidates,
    }
    errors: list[str] = []
    warnings: list[str] = []

    if marker.get("decision") != "PASS_MARKER_SYNCED_030A2":
        errors.append("Marker sync is not PASS.")
    for name, ok in checks.items():
        if not ok:
            if name in {"no_real_secret_findings", "pypirc_absent", "token_file_candidates_absent"}:
                errors.append(f"{name} failed.")
            else:
                warnings.append(f"{name} failed.")

    if not checks["no_real_secret_findings"] or not checks["pypirc_absent"] or not checks["token_file_candidates_absent"]:
        decision = "BLOCK_SECRET_FINDING"
    elif not checks["claim_guard_pass"]:
        decision = "BLOCK_OVERCLAIM"
    elif not checks["tech_protection_pass"]:
        decision = "BLOCK_PRIVATE_KERNEL_EXPOSURE"
    elif tracked_publishers:
        decision = "BLOCK_MCP_PUBLISHER_BINARY_COMMITTED"
    elif tracked_dist:
        decision = "HOLD_DIST_FILES_COMMITTED"
    elif not all(checks.values()) or marker.get("decision") != "PASS_MARKER_SYNCED_030A2":
        decision = "HOLD_FINAL_PREFLIGHT_INCOMPLETE"
    else:
        decision = "PASS_READY_FOR_FINAL_PYPI_UPLOAD"

    result = {
        "schema": "AOI_030A2FinalPreflightResult/v0.1",
        "generated_at": now(),
        "decision": decision,
        "target_version": TARGET_VERSION,
        "package_name": PACKAGE_NAME,
        "mcp_name": CANONICAL_MCP_NAME,
        "marker_sync_decision": marker.get("decision"),
        "marker_state": state,
        "checks": checks,
        "missing_rest_paths": missing_rest,
        "missing_mcp_tools": missing_mcp,
        "package_data_audit_decision": package_data.get("decision"),
        "agent_surface_audit_decision": surface.get("decision"),
        "final_build_decision": build.get("decision"),
        "no_secrets_overall": no_secrets.get("overall_token"),
        "no_secrets_real_findings": int(no_secrets.get("finding_count", 0) or 0),
        "no_secrets_warnings": int(no_secrets.get("warning_count", 0) or 0),
        "claim_guard_decision": claim.get("overall_token"),
        "claim_guard_risky_phrase_count": int(claim.get("risky_phrase_count", 0) or 0),
        "tech_protection_decision": tech.get("decision"),
        "public_private_alignment_decision": alignment.get("decision"),
        "dist_release_files_committed": tracked_dist,
        "pypirc_exists": pypirc_exists(),
        "mcp_publisher_binary_committed": tracked_publishers,
        "token_file_candidates": token_candidates,
        "pypi_upload_performed": False,
        "mcp_registry_publish_performed": False,
        "token_printed": False,
        "can_claim_certification": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(FINAL_PREFLIGHT_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_final_preflight()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"aoi_030a2_final_preflight: {result['decision']} token_printed=False")


if __name__ == "__main__":
    main()

