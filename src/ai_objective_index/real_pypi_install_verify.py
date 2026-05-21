from __future__ import annotations

import json
import shutil
import subprocess
import sys
import venv
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .real_pypi_upload_gate import PACKAGE_NAME, TARGET_VERSION, _repo_root, _sanitize
from .real_pypi_upload_runner import OUTPUT_PATH as UPLOAD_RESULT_PATH


OUTPUT_PATH = Path("public_launch") / "wave10_real_pypi" / "REAL_PYPI_INSTALL_VERIFY_RESULT.json"
TEMP_VENV_PATH = Path("data") / "generated" / "real_pypi_install_tmp" / "aoi_real_pypi_verify"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _venv_python(path: Path) -> Path:
    if sys.platform.startswith("win"):
        return path / "Scripts" / "python.exe"
    return path / "bin" / "python"


def _run(command: list[str], timeout: int = 600) -> dict[str, Any]:
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


def _create_venv(path: Path) -> dict[str, Any]:
    if path.exists():
        shutil.rmtree(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        venv.EnvBuilder(with_pip=True, clear=True).create(path)
    except OSError as exc:
        return {"ok": False, "error": _sanitize(exc)}
    return {"ok": True, "path": str(path.relative_to(_repo_root()))}


def _cleanup_venv(path: Path) -> bool:
    try:
        if path.exists():
            shutil.rmtree(path)
    except OSError:
        return False
    return True


def run_real_pypi_install_verify(
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    upload_result: dict[str, Any] | None = None,
    create_venv: Callable[[Path], dict[str, Any]] = _create_venv,
    cleanup_venv: Callable[[Path], bool] = _cleanup_venv,
    write_result: bool = True,
) -> dict[str, Any]:
    upload_result = upload_result if upload_result is not None else _read_json(UPLOAD_RESULT_PATH)
    upload_token = upload_result.get("result_token")
    errors: list[str] = []
    warnings: list[str] = []
    steps: dict[str, Any] = {}
    temp_venv = _repo_root() / TEMP_VENV_PATH
    cleaned = False

    if upload_token not in {"UPLOAD_SUCCESS", "HOLD_ALREADY_EXISTS"}:
        decision = "HOLD_PYPI_PACKAGE_NOT_FOUND"
        warnings.append("Real PyPI upload has not been confirmed, so install verification was not attempted.")
    else:
        created = create_venv(temp_venv)
        steps["create_venv"] = created
        if not created.get("ok"):
            decision = "BLOCK_INSTALL_FAILED"
            errors.append("Temporary virtual environment creation failed.")
        else:
            python_exe = _venv_python(temp_venv)
            install = runner([str(python_exe), "-m", "pip", "install", f"{PACKAGE_NAME}=={TARGET_VERSION}"], 900)
            steps["pip_install"] = install
            if not install.get("ok"):
                text = (str(install.get("stdout", "")) + "\n" + str(install.get("stderr", ""))).lower()
                if "no matching distribution" in text or "could not find a version" in text:
                    decision = "HOLD_PYPI_PACKAGE_NOT_FOUND"
                elif "resolution" in text or "conflict" in text:
                    decision = "HOLD_DEPENDENCY_RESOLUTION_FAILED"
                else:
                    decision = "BLOCK_INSTALL_FAILED"
                errors.append("Real PyPI package install failed.")
            else:
                import_check = runner(
                    [
                        str(python_exe),
                        "-c",
                        "import ai_objective_index; print(ai_objective_index.__version__)",
                    ],
                    120,
                )
                steps["import_check"] = import_check
                if not import_check.get("ok") or TARGET_VERSION not in str(import_check.get("stdout", "")):
                    decision = "BLOCK_IMPORT_FAILED"
                    errors.append("Installed package import/version check failed.")
                else:
                    smoke = runner([str(python_exe), "-m", "ai_objective_index.mcp_smoke"], 300)
                    route_demo = runner(
                        [
                            str(python_exe),
                            "-m",
                            "ai_objective_index.vnext.objective_router_cli_demo",
                            "--query",
                            "browser automation MCP server",
                            "--objective",
                            "select source-traced MCP candidates",
                            "--data-scope",
                            "public_beta_mcp",
                            "--limit",
                            "3",
                        ],
                        300,
                    )
                    probe_demo = runner(
                        [
                            str(python_exe),
                            "-m",
                            "ai_objective_index.vnext.probe_cli_demo",
                            "--query",
                            "browser automation MCP server",
                            "--objective",
                            "select source-traced MCP candidates",
                            "--data-scope",
                            "public_beta_mcp",
                            "--limit",
                            "3",
                        ],
                        300,
                    )
                    steps["mcp_smoke"] = smoke
                    steps["objective_router_demo"] = route_demo
                    steps["probe_demo"] = probe_demo
                    if not smoke.get("ok") or not route_demo.get("ok") or not probe_demo.get("ok"):
                        decision = "BLOCK_SMOKE_FAILED"
                        errors.append("One or more installed-package smoke checks failed.")
                    else:
                        decision = "PASS_REAL_PYPI_INSTALL"
        cleaned = cleanup_venv(temp_venv)
        if not cleaned:
            warnings.append(f"Temporary venv cleanup could not be confirmed: {TEMP_VENV_PATH}")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "target_version": TARGET_VERSION,
        "package_name": PACKAGE_NAME,
        "upload_result_token": upload_token,
        "steps": steps,
        "temp_venv_path": str(TEMP_VENV_PATH),
        "temp_venv_cleaned": cleaned,
        "external_api_keys_required": False,
        "live_mcp_calls_performed": False,
        "external_tool_execution_performed": False,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_real_pypi_install_verify()
    print(
        "real_pypi_install_verify: "
        f"{result['decision']} "
        "token_printed=False"
    )


if __name__ == "__main__":
    main()
