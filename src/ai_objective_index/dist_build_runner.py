from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


WAVE3_DIR = Path("public_launch") / "wave3"
DIST_RESULT_PATH = WAVE3_DIR / "DIST_BUILD_RESULT.json"
TWINE_RESULT_PATH = WAVE3_DIR / "TWINE_CHECK_RESULT.json"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _sanitize(value: Any) -> str:
    text = str(value or "")
    lowered = text.lower()
    for marker in ["pypi-", "ghp_", "gho_", "github_pat_", "hf_", "password=", "api_key=", "bearer "]:
        index = lowered.find(marker)
        if index >= 0:
            return text[:index] + "[redacted]"
    return text[:1600]


def _run(command: list[str], timeout: int = 300) -> dict[str, Any]:
    try:
        tmp_dir = _repo_root() / "data" / "generated" / "build_tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env["TMP"] = str(tmp_dir)
        env["TEMP"] = str(tmp_dir)
        env["TMPDIR"] = str(tmp_dir)
        completed = subprocess.run(
            command,
            cwd=_repo_root(),
            env=env,
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
    for path in sorted(list(dist.glob("ai_objective_index-*.whl")) + list(dist.glob("ai_objective_index-*.tar.gz"))):
        files.append({"path": str(path.relative_to(_repo_root())), "size_bytes": path.stat().st_size})
    return files


def _remove_old_aoi_dist_artifacts() -> list[str]:
    dist = _repo_root() / "dist"
    removed: list[str] = []
    if not dist.exists():
        return removed
    for path in sorted(list(dist.glob("ai_objective_index-*.whl")) + list(dist.glob("ai_objective_index-*.tar.gz"))):
        path.unlink()
        removed.append(str(path.relative_to(_repo_root())))
    return removed


def run_dist_build(
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    clean_old: bool = True,
    write_result: bool = True,
) -> dict[str, Any]:
    build_available = _module_available("build")
    twine_available = _module_available("twine")
    removed = _remove_old_aoi_dist_artifacts() if clean_old else []
    errors: list[str] = []
    warnings: list[str] = []
    build_result: dict[str, Any] = {"ok": False, "skipped": True}
    twine_result: dict[str, Any] = {"ok": False, "status": "NOT_CHECKED"}
    dist_files: list[dict[str, Any]] = []

    if not build_available:
        decision = "HOLD_BUILD_TOOL_MISSING"
        warnings.append("Python build module is unavailable.")
    else:
        build_result = runner([sys.executable, "-m", "build", "--sdist", "--wheel", "--no-isolation"], 600)
        dist_files = _dist_files()
        wheel_count = sum(1 for item in dist_files if item["path"].endswith(".whl"))
        sdist_count = sum(1 for item in dist_files if item["path"].endswith(".tar.gz"))
        if not build_result.get("ok") or wheel_count == 0 or sdist_count == 0:
            decision = "BLOCK_BUILD_FAILED"
            errors.append("Build failed or did not create both wheel and sdist.")
        elif not twine_available:
            decision = "HOLD_TWINE_MISSING"
            warnings.append("twine is unavailable; twine check was not run.")
        else:
            twine_result = runner([sys.executable, "-m", "twine", "check", *[item["path"] for item in dist_files]], 180)
            if not twine_result.get("ok"):
                decision = "BLOCK_TWINE_CHECK_FAILED"
                errors.append("twine check failed.")
            else:
                decision = "PASS_BUILD_READY"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "build_available": build_available,
        "twine_available": twine_available,
        "old_aoi_dist_artifacts_removed": removed,
        "build_result": build_result,
        "dist_files": dist_files,
        "errors": errors,
        "warnings": warnings,
        "upload_performed": False,
        "testpypi_upload_performed": False,
        "pypi_upload_performed": False,
        "token_printed": False,
    }
    twine_payload = {
        "generated_at": result["generated_at"],
        "decision": "PASS_TWINE_CHECK" if twine_result.get("ok") else ("HOLD_TWINE_MISSING" if not twine_available else "BLOCK_TWINE_CHECK_FAILED"),
        "twine_available": twine_available,
        "twine_result": twine_result,
        "dist_files_checked": dist_files if twine_result.get("ok") else [],
        "upload_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(DIST_RESULT_PATH, result)
        _write_json(TWINE_RESULT_PATH, twine_payload)
    return result


def main() -> None:
    result = run_dist_build()
    print(
        "dist_build_runner: "
        f"{result['decision']} "
        f"dist_files={len(result['dist_files'])} "
        "upload_performed=False"
    )


if __name__ == "__main__":
    main()
