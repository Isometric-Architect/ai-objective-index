from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .package_metadata_audit import run_package_metadata_audit


WAVE2_DIR = Path("public_launch") / "wave2"
OUTPUT_PATH = WAVE2_DIR / "PYPI_PUBLISH_READINESS_RESULT.json"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _sanitize(value: Any) -> str:
    text = str(value or "")
    for marker in ["pypi-", "ghp_", "gho_", "github_pat_", "hf_", "password=", "api_key="]:
        index = text.lower().find(marker.lower())
        if index >= 0:
            return text[:index] + "[redacted]"
    return text[:1000]


def _run(command: list[str], timeout: int = 180) -> dict[str, Any]:
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
        return {
            "command": command,
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": _sanitize(completed.stdout),
            "stderr": _sanitize(completed.stderr),
        }
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"command": command, "ok": False, "returncode": None, "stdout": "", "stderr": _sanitize(exc)}


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _dist_files() -> list[dict[str, Any]]:
    dist = _repo_root() / "dist"
    if not dist.exists():
        return []
    files: list[dict[str, Any]] = []
    for path in sorted(list(dist.glob("*.whl")) + list(dist.glob("*.tar.gz"))):
        files.append({"path": str(path.relative_to(_repo_root())), "size_bytes": path.stat().st_size})
    return files


def _run_mcp_smoke(runner: Callable[[list[str], int], dict[str, Any]]) -> dict[str, Any]:
    return runner([sys.executable, "-m", "ai_objective_index.mcp_smoke"], 120)


def run_pypi_publish_readiness(
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
) -> dict[str, Any]:
    metadata = run_package_metadata_audit(write_result=True)
    errors: list[str] = []
    warnings: list[str] = []
    build_available = _module_available("build")
    twine_available = _module_available("twine") or bool(shutil.which("twine"))
    build_result: dict[str, Any] = {"ok": False, "skipped": True}
    twine_result: dict[str, Any] = {"ok": False, "status": "NOT_CHECKED"}
    smoke_result: dict[str, Any] = {"ok": False, "status": "NOT_CHECKED"}

    if metadata.get("overall_token") != "PASS":
        errors.append("Package metadata audit did not pass.")

    if not build_available:
        decision = "HOLD_BUILD_TOOL_MISSING"
        warnings.append("Python build module is not installed; run python -m pip install build locally if packaging is desired.")
    else:
        build_result = runner([sys.executable, "-m", "build", "--sdist", "--wheel", "--no-isolation"], 240)
        if not build_result.get("ok"):
            decision = "HOLD_BUILD_TOOL_MISSING"
            warnings.append("Local package build failed.")
        else:
            dist_files = _dist_files()
            if twine_available:
                twine_cmd = ["twine", "check", *[item["path"] for item in dist_files]] if shutil.which("twine") else [sys.executable, "-m", "twine", "check", *[item["path"] for item in dist_files]]
                twine_result = runner(twine_cmd, 120)
                if not twine_result.get("ok"):
                    decision = "HOLD_TWINE_MISSING"
                    warnings.append("twine check failed or was unavailable.")
                else:
                    decision = "PASS_BUILD_READY"
            else:
                decision = "HOLD_TWINE_MISSING"
                warnings.append("twine is not installed; twine check was not run.")
            smoke_result = _run_mcp_smoke(runner)
            if not smoke_result.get("ok"):
                warnings.append("MCP smoke command did not pass in current environment.")

    if metadata.get("token_like_findings"):
        decision = "BLOCK_SECRET_FINDING"
        errors.append("Token-like strings found in package metadata.")
    elif metadata.get("overall_token") != "PASS":
        decision = "BLOCK_INVALID_METADATA"

    dist_files = _dist_files()
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "build_tool_available": build_available,
        "twine_available": twine_available,
        "build_result": build_result,
        "twine_result": twine_result,
        "local_install_check": "NOT_CHECKED_NO_NETWORK_FREE_TEMP_INSTALL",
        "mcp_smoke_result": {
            "ok": bool(smoke_result.get("ok")),
            "stdout": smoke_result.get("stdout", ""),
            "stderr": smoke_result.get("stderr", ""),
        },
        "dist_files": dist_files,
        "errors": errors,
        "warnings": warnings,
        "upload_performed": False,
        "testpypi_upload_performed": False,
        "pypi_upload_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_pypi_publish_readiness()
    print(
        "pypi_publish_readiness: "
        f"{result['decision']} "
        f"dist_files={len(result['dist_files'])} "
        "upload_performed=False"
    )


if __name__ == "__main__":
    main()
