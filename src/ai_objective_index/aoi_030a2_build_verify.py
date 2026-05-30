from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .aoi_030a2_marker_sync import (
    CANONICAL_MCP_NAME,
    MCP_MARKER,
    OUTPUT_DIR,
    SDIST_PATH,
    TARGET_VERSION,
    WHEEL_PATH,
    repo_root,
    run_marker_sync,
    write_json,
)


OUTPUT_PATH = OUTPUT_DIR / "AOI_030A2_BUILD_VERIFY_RESULT.json"


def sanitize(text: Any) -> str:
    value = str(text or "")
    for marker in ["pypi-", "ghp_", "gho_", "github_pat_", "hf_", "Bearer "]:
        value = value.replace(marker, f"{marker}[redacted]")
    return value[:4000]


def _run(command: list[str], timeout: int = 600) -> dict[str, Any]:
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


def _artifact_contains_marker(path: Path) -> bool:
    full = repo_root() / path
    if not full.exists():
        return False
    if full.suffix == ".whl":
        try:
            with zipfile.ZipFile(full) as archive:
                for name in archive.namelist():
                    if name.endswith("METADATA") or name.endswith("README.md"):
                        if MCP_MARKER in archive.read(name).decode("utf-8", errors="ignore"):
                            return True
        except (OSError, zipfile.BadZipFile):
            return False
    if full.suffixes[-2:] == [".tar", ".gz"]:
        try:
            with tarfile.open(full, "r:gz") as archive:
                for member in archive.getmembers():
                    if member.isfile() and (member.name.endswith("PKG-INFO") or member.name.endswith("README.md")):
                        stream = archive.extractfile(member)
                        if stream and MCP_MARKER in stream.read().decode("utf-8", errors="ignore"):
                            return True
        except (OSError, tarfile.TarError):
            return False
    return False


def run_build_verify(
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    run_build: bool = True,
    write_result: bool = True,
) -> dict[str, Any]:
    marker = run_marker_sync(write_result=True)
    errors: list[str] = []
    warnings: list[str] = []
    build_result: dict[str, Any] = {"skipped": True, "ok": False}
    twine_result: dict[str, Any] = {"skipped": True, "ok": False}

    if marker.get("decision") != "PASS_MARKER_SYNCED_030A2":
        errors.append("Marker/version sync is not PASS.")
    elif run_build:
        build_result = runner([sys.executable, "-m", "build"], 900)
    else:
        warnings.append("Build command skipped by caller.")

    wheel_exists = (repo_root() / WHEEL_PATH).exists()
    sdist_exists = (repo_root() / SDIST_PATH).exists()
    if wheel_exists and sdist_exists:
        twine_result = runner([sys.executable, "-m", "twine", "check", str(WHEEL_PATH), str(SDIST_PATH)], 300)
    else:
        warnings.append("Expected 0.3.0a2 wheel/sdist are missing.")

    wheel_marker = _artifact_contains_marker(WHEEL_PATH)
    sdist_marker = _artifact_contains_marker(SDIST_PATH)
    if not wheel_marker or not sdist_marker:
        errors.append("Built artifacts do not both contain the canonical mcp-name marker.")
    if run_build and not build_result.get("ok"):
        errors.append("python -m build failed.")
    if not twine_result.get("ok"):
        errors.append("twine check failed or did not run.")

    decision = "PASS_BUILD_TWINE_MARKER_SYNCED" if not errors else "HOLD_BUILD_VERIFY_FAILED"
    result = {
        "schema": "AOI_030A2BuildVerifyResult/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "target_version": TARGET_VERSION,
        "canonical_mcp_name": CANONICAL_MCP_NAME,
        "wheel_path": str(WHEEL_PATH),
        "sdist_path": str(SDIST_PATH),
        "wheel_exists": wheel_exists,
        "sdist_exists": sdist_exists,
        "wheel_marker_matches": wheel_marker,
        "sdist_marker_matches": sdist_marker,
        "build_result": build_result,
        "twine_check": twine_result,
        "token_printed": False,
        "upload_performed": False,
        "mcp_registry_submission_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_build_verify()
    print(
        "aoi_030a2_build_verify: "
        f"{result['decision']} wheel={result['wheel_exists']} sdist={result['sdist_exists']}"
    )


if __name__ == "__main__":
    main()
