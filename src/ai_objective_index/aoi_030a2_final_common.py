from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .aoi_030a2_build_verify import OUTPUT_PATH as BUILD_VERIFY_OUTPUT_PATH
from .aoi_030a2_build_verify import sanitize
from .aoi_030a2_marker_sync import (
    CANONICAL_MCP_NAME,
    MCP_MARKER,
    OUTPUT_DIR as RECOVERY_OUTPUT_DIR,
    PACKAGE_NAME,
    SDIST_PATH,
    TARGET_VERSION,
    WHEEL_PATH,
    repo_root,
    read_json as read_repo_json,
    write_json as write_repo_json,
)


FINAL_OUTPUT_DIR = Path("public_launch") / "aoi_030a2_final_publish"
FINAL_PREFLIGHT_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_FINAL_PREFLIGHT_RESULT.json"
FINAL_BUILD_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_FINAL_BUILD_RESULT.json"
FINAL_PYPI_UPLOAD_GATE_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_FINAL_PYPI_UPLOAD_GATE_RESULT.json"
FINAL_PYPI_UPLOAD_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_FINAL_PYPI_UPLOAD_RESULT.json"
FINAL_PYPI_VERIFY_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_FINAL_PYPI_VERIFY_RESULT.json"
FINAL_MCP_GATE_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_FINAL_MCP_REGISTRY_GATE_RESULT.json"
FINAL_MCP_PUBLISH_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_FINAL_MCP_REGISTRY_PUBLISH_RESULT.json"
FINAL_MCP_RECONCILE_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_FINAL_MCP_REGISTRY_RECONCILE_RESULT.json"
FINAL_REPORT_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_FINAL_PUBLISH_REPORT.md"
TOKEN_SAFETY_NOTE_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_TOKEN_SAFETY_NOTE.md"
FAILURE_RECOVERY_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_FAILURE_RECOVERY.md"
NEXT_ACTIONS_PATH = FINAL_OUTPUT_DIR / "AOI_030A2_NEXT_ACTIONS.md"

CONFIRM_PYPI_ENV = "AOI_REAL_PYPI_UPLOAD_CONFIRM"
CONFIRM_MCP_ENV = "AOI_MCP_REGISTRY_SUBMIT_CONFIRM"

TOKEN_FILE_PATTERNS = [
    re.compile(r"(^|/)\.pypirc$", re.I),
    re.compile(r"(^|/)\.env(\.|$)", re.I),
    re.compile(r"(^|/)(credentials?|secrets?|private_key)(\.|/|$)", re.I),
]


def now() -> str:
    return datetime.now(UTC).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    return write_repo_json(path, payload)


def read_json(path: Path) -> dict[str, Any]:
    return read_repo_json(path)


def read_text(path: Path) -> str:
    full = repo_root() / path
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")


def git_ls_files() -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-c", "safe.directory=C:/Users/Isometric-Architect/Desktop/ai_objective_index", "ls-files"],
            cwd=repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return []
    if completed.returncode != 0:
        return []
    return [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]


def committed_release_dist_files() -> list[str]:
    tracked = git_ls_files()
    return [
        path
        for path in tracked
        if path.startswith("dist/")
        and (path.endswith(".whl") or path.endswith(".tar.gz") or f"ai_objective_index-{TARGET_VERSION}" in path)
    ]


def committed_mcp_publisher_binaries() -> list[str]:
    tracked = git_ls_files()
    return [
        path
        for path in tracked
        if "mcp-publisher" in path.lower() and (path.lower().endswith(".exe") or path.lower().endswith("/mcp-publisher"))
    ]


def token_file_candidates() -> list[str]:
    return [path for path in git_ls_files() if any(pattern.search(path) for pattern in TOKEN_FILE_PATTERNS)]


def pypirc_exists() -> bool:
    return (repo_root() / ".pypirc").exists()


def dist_paths_exist() -> dict[str, bool]:
    return {
        "wheel_exists": (repo_root() / WHEEL_PATH).exists(),
        "sdist_exists": (repo_root() / SDIST_PATH).exists(),
    }


def write_final_build_result() -> dict[str, Any]:
    build = read_json(BUILD_VERIFY_OUTPUT_PATH)
    local_smoke = build.get("local_install_smoke", {}) if isinstance(build.get("local_install_smoke"), dict) else {}
    mcp_smoke = local_smoke.get("mcp_smoke_result", {}) if isinstance(local_smoke.get("mcp_smoke_result"), dict) else {}
    mcp_validate = local_smoke.get("mcp_publisher_validate", {}) if isinstance(local_smoke.get("mcp_publisher_validate"), dict) else {}
    if build.get("decision") == "PASS_BUILD_TWINE_MARKER_SYNCED":
        decision = "PASS_FINAL_BUILD_READY"
    elif build:
        decision = "HOLD_FINAL_BUILD_NOT_READY"
    else:
        decision = "HOLD_FINAL_BUILD_NOT_RUN"
    result = {
        "schema": "AOI_030A2FinalBuildResult/v0.1",
        "generated_at": now(),
        "decision": decision,
        "source_build_result": str(BUILD_VERIFY_OUTPUT_PATH).replace("\\", "/"),
        "source_build_decision": build.get("decision"),
        "target_version": TARGET_VERSION,
        "wheel_path": str(WHEEL_PATH).replace("\\", "/"),
        "sdist_path": str(SDIST_PATH).replace("\\", "/"),
        **dist_paths_exist(),
        "twine_check_passed": build.get("twine_check", {}).get("ok") is True,
        "local_install_smoke_passed": local_smoke.get("ok") is True,
        "mcp_smoke_passed": mcp_smoke.get("ok") is True,
        "mcp_publisher_validate_passed": mcp_validate.get("ok") is True,
        "pypi_upload_performed": False,
        "mcp_registry_publish_performed": False,
        "token_printed": False,
        "errors": [] if decision == "PASS_FINAL_BUILD_READY" else ["Build verifier has not produced a final PASS."],
        "warnings": [],
    }
    write_json(FINAL_BUILD_PATH, result)
    return result


def redact_command_result(payload: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(payload)
    for key in ["stdout", "stderr", "error"]:
        if key in redacted:
            redacted[key] = sanitize(redacted[key])
    return redacted
