from __future__ import annotations

import json
import shutil
import subprocess
import sys
import venv
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .aoi_030a2_build_verify import sanitize
from .aoi_030a2_marker_sync import OUTPUT_DIR, PACKAGE_NAME, TARGET_VERSION, repo_root, read_json, write_json
from .aoi_030a2_pypi_upload_gate import OUTPUT_PATH as UPLOAD_OUTPUT_PATH


OUTPUT_PATH = OUTPUT_DIR / "AOI_030A2_PYPI_VERIFY_RESULT.json"
TEMP_VENV_PATH = Path("data") / "generated" / "aoi_030a2_verify_tmp" / "venv"
UPLOAD_OK = {"PASS_PYPI_UPLOAD_COMPLETED", "HOLD_VERSION_ALREADY_EXISTS"}


def _venv_python(path: Path) -> Path:
    return path / "Scripts" / "python.exe" if sys.platform.startswith("win") else path / "bin" / "python"


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


def _create_venv(path: Path) -> dict[str, Any]:
    if path.exists():
        shutil.rmtree(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        venv.EnvBuilder(with_pip=True, clear=True).create(path)
    except OSError as exc:
        return {"ok": False, "error": sanitize(exc)}
    return {"ok": True, "path": str(path.relative_to(repo_root()))}


def _cleanup(path: Path) -> bool:
    try:
        if path.exists():
            shutil.rmtree(path)
    except OSError:
        return False
    return True


def run_pypi_verify(
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    upload_result: dict[str, Any] | None = None,
    create_venv: Callable[[Path], dict[str, Any]] = _create_venv,
    cleanup_venv: Callable[[Path], bool] = _cleanup,
    write_result: bool = True,
) -> dict[str, Any]:
    upload_result = upload_result if upload_result is not None else read_json(UPLOAD_OUTPUT_PATH)
    upload_decision = upload_result.get("decision")
    temp_venv = repo_root() / TEMP_VENV_PATH
    errors: list[str] = []
    warnings: list[str] = []
    steps: dict[str, Any] = {}
    cleaned = False

    if upload_decision not in UPLOAD_OK:
        decision = "HOLD_PYPI_UPLOAD_NOT_CONFIRMED"
        warnings.append("PyPI upload/version availability has not been confirmed for 0.3.0a2.")
    else:
        created = create_venv(temp_venv)
        steps["create_venv"] = created
        if not created.get("ok"):
            decision = "BLOCK_INSTALL_FAILED"
            errors.append("Temporary venv creation failed.")
        else:
            python_exe = _venv_python(temp_venv)
            install = runner([str(python_exe), "-m", "pip", "install", f"{PACKAGE_NAME}=={TARGET_VERSION}"], 900)
            steps["pip_install"] = install
            import_check = {"ok": False, "stdout": "", "stderr": "", "command": []}
            smoke = {"ok": False, "stdout": "", "stderr": "", "command": []}
            if install.get("ok"):
                import_check = runner(
                    [str(python_exe), "-c", "import ai_objective_index; print(ai_objective_index.__version__)"],
                    120,
                )
                smoke = runner([str(python_exe), "-m", "ai_objective_index.mcp_smoke"], 300)
            steps["import_check"] = import_check
            steps["mcp_smoke"] = smoke
            if not install.get("ok"):
                decision = "HOLD_PYPI_PACKAGE_NOT_FOUND"
                errors.append("Package install from PyPI failed.")
            elif TARGET_VERSION not in str(import_check.get("stdout", "")):
                decision = "BLOCK_IMPORT_VERSION_MISMATCH"
                errors.append("Installed package version did not match 0.3.0a2.")
            elif not smoke.get("ok"):
                decision = "BLOCK_SMOKE_FAILED"
                errors.append("Installed package smoke check failed.")
            else:
                decision = "PASS_PYPI_030A2_VERIFIED"
        cleaned = cleanup_venv(temp_venv)
        if not cleaned:
            warnings.append("Temporary verification venv cleanup could not be confirmed.")

    result = {
        "schema": "AOI_030A2PyPIVerifyResult/v0.1",
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "target_version": TARGET_VERSION,
        "package_name": PACKAGE_NAME,
        "upload_decision": upload_decision,
        "steps": steps,
        "temp_venv_path": str(TEMP_VENV_PATH),
        "temp_venv_cleaned": cleaned,
        "token_printed": False,
        "external_api_keys_required": False,
        "live_mcp_calls_performed": False,
        "mcp_registry_submission_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_pypi_verify()
    print(f"aoi_030a2_pypi_verify: {result['decision']} token_printed=False")


if __name__ == "__main__":
    main()
