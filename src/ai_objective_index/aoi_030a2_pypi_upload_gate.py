from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .aoi_030a2_build_verify import OUTPUT_PATH as BUILD_OUTPUT_PATH, sanitize
from .aoi_030a2_marker_sync import (
    OUTPUT_DIR,
    PACKAGE_NAME,
    SDIST_PATH,
    TARGET_VERSION,
    WHEEL_PATH,
    repo_root,
    read_json,
    run_marker_sync,
    write_json,
)


OUTPUT_PATH = OUTPUT_DIR / "AOI_030A2_PYPI_UPLOAD_RESULT.json"
PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
CONFIRM_ENV = "AOI_REAL_PYPI_UPLOAD_CONFIRM"
TOKEN_PATTERNS = [
    re.compile(r"pypi-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"gho_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]


def _pypi_status(timeout: int = 20) -> dict[str, Any]:
    request = urllib.request.Request(PYPI_JSON_URL, headers={"User-Agent": "ai-objective-index-aoi-030a2"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"checked": True, "status": "PROJECT_AVAILABLE_OR_NEW", "versions": []}
        return {"checked": False, "status": "HOLD_PYPI_STATUS_NOT_CHECKED", "error": f"HTTP {exc.code}", "versions": []}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, UnicodeError) as exc:
        return {"checked": False, "status": "HOLD_PYPI_STATUS_NOT_CHECKED", "error": sanitize(exc), "versions": []}
    releases = payload.get("releases", {}) if isinstance(payload, dict) else {}
    versions = sorted(str(item) for item in releases) if isinstance(releases, dict) else []
    return {
        "checked": True,
        "status": "HOLD_VERSION_ALREADY_EXISTS" if TARGET_VERSION in versions else "PASS_VERSION_AVAILABLE",
        "versions": versions,
    }


def tracked_token_findings() -> list[str]:
    findings: list[str] = []
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
        return findings
    for raw in completed.stdout.splitlines():
        normalized = raw.replace("\\", "/")
        path = repo_root() / raw
        if not path.exists() or path.is_dir() or path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if normalized.startswith("tests/"):
            continue
        if any(pattern.search(text) for pattern in TOKEN_PATTERNS):
            findings.append(normalized)
    return findings


def _run_upload(command: list[str], timeout: int = 900) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, cwd=repo_root(), timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": sanitize(exc)}
    return {"ok": completed.returncode == 0, "returncode": completed.returncode, "stdout": "", "stderr": ""}


def upload_command() -> list[str]:
    return [sys.executable, "-m", "twine", "upload", str(WHEEL_PATH), str(SDIST_PATH)]


def run_pypi_upload_gate(
    env: dict[str, str] | None = None,
    pypi_checker: Callable[[], dict[str, Any]] = _pypi_status,
    token_scanner: Callable[[], list[str]] = tracked_token_findings,
    upload_runner: Callable[[list[str], int], dict[str, Any]] = _run_upload,
    write_result: bool = True,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    marker = run_marker_sync(write_result=True)
    build = read_json(BUILD_OUTPUT_PATH)
    pypi = pypi_checker()
    token_findings = token_scanner()
    pypirc_exists = (repo_root() / ".pypirc").exists()
    wheel_exists = (repo_root() / WHEEL_PATH).exists()
    sdist_exists = (repo_root() / SDIST_PATH).exists()
    env_confirm_present = env_map.get(CONFIRM_ENV) == "YES"
    errors: list[str] = []
    warnings: list[str] = []
    upload_result: dict[str, Any] = {"skipped": True, "ok": False}
    upload_performed = False

    if marker.get("decision") != "PASS_MARKER_SYNCED_030A2":
        errors.append("Marker sync is not PASS.")
    if build.get("decision") != "PASS_BUILD_TWINE_MARKER_SYNCED":
        errors.append("Build/twine verification is not PASS.")
    if not wheel_exists or not sdist_exists:
        errors.append("0.3.0a2 dist files are missing.")
    if pypirc_exists or token_findings:
        errors.append("Token file or token-like tracked content found.")
    if pypi.get("status") == "HOLD_VERSION_ALREADY_EXISTS":
        warnings.append("PyPI already has 0.3.0a2; do not upload duplicate files.")
    if not pypi.get("checked"):
        warnings.append("PyPI version availability could not be checked.")

    if token_findings or pypirc_exists:
        decision = "BLOCK_SECRET_FINDING"
    elif errors:
        decision = "BLOCK_UPLOAD_GATE_FAILED"
    elif pypi.get("status") == "HOLD_VERSION_ALREADY_EXISTS":
        decision = "HOLD_VERSION_ALREADY_EXISTS"
    elif not pypi.get("checked"):
        decision = "HOLD_PYPI_STATUS_NOT_CHECKED"
    elif not env_confirm_present:
        decision = "HOLD_ENV_CONFIRM_REQUIRED"
        warnings.append(f"{CONFIRM_ENV}=YES is required before interactive twine upload.")
    else:
        upload_result = upload_runner(upload_command(), 900)
        upload_performed = bool(upload_result.get("ok"))
        decision = "PASS_PYPI_UPLOAD_COMPLETED" if upload_performed else "BLOCK_UPLOAD_FAILED"

    result = {
        "schema": "AOI_030A2PyPIUploadResult/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "target_version": TARGET_VERSION,
        "package_name": PACKAGE_NAME,
        "wheel_path": str(WHEEL_PATH),
        "sdist_path": str(SDIST_PATH),
        "wheel_exists": wheel_exists,
        "sdist_exists": sdist_exists,
        "build_decision": build.get("decision"),
        "pypi_status": pypi,
        "env_confirm_present": env_confirm_present,
        "command_redacted": " ".join(upload_command()),
        "upload_result": upload_result,
        "upload_performed": upload_performed,
        "pypirc_exists": pypirc_exists,
        "token_like_tracked_findings": token_findings,
        "token_printed": False,
        "testpypi_used": False,
        "mcp_registry_submission_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_pypi_upload_gate()
    print(
        "aoi_030a2_pypi_upload_gate: "
        f"{result['decision']} upload_performed={result['upload_performed']} token_printed=False"
    )


if __name__ == "__main__":
    main()
