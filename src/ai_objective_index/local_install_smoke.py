from __future__ import annotations

import json
import shutil
import subprocess
import sys
import venv
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


WAVE9_DIR = Path("public_launch") / "wave9"
OUTPUT_PATH = WAVE9_DIR / "LOCAL_INSTALL_SMOKE_RESULT.json"
DEFAULT_VENV_PATH = Path("data/generated/test_install_tmp/aoi_pkg_smoke")


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


def _run(command: list[str], timeout: int = 300, cwd: Path | None = None) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd or _repo_root(),
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


def _wheel_path() -> Path | None:
    wheels = sorted((_repo_root() / "dist").glob("ai_objective_index-*.whl"))
    return wheels[-1] if wheels else None


def _venv_python(venv_path: Path) -> Path:
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def run_local_install_smoke(
    runner: Callable[[list[str], int, Path | None], dict[str, Any]] = _run,
    venv_path: Path | None = None,
    create_venv: Callable[[Path], None] | None = None,
    cleanup: bool = True,
    write_result: bool = True,
) -> dict[str, Any]:
    root = _repo_root()
    venv_rel = venv_path or DEFAULT_VENV_PATH
    venv_full = venv_rel if venv_rel.is_absolute() else root / venv_rel
    wheel = _wheel_path()
    errors: list[str] = []
    warnings: list[str] = []
    install_result: dict[str, Any] = {"ok": False, "skipped": True}
    import_result: dict[str, Any] = {"ok": False, "skipped": True}
    smoke_result: dict[str, Any] = {"ok": False, "skipped": True}
    vnext_smoke_result: dict[str, Any] = {"ok": False, "skipped": True}
    probe_smoke_result: dict[str, Any] = {"ok": False, "skipped": True}
    console_smoke_result: dict[str, Any] = {"ok": False, "skipped": True}

    if wheel is None:
        decision = "HOLD_DIST_MISSING"
        errors.append("No built wheel found in dist/.")
    else:
        try:
            if venv_full.exists():
                shutil.rmtree(venv_full)
            venv_full.parent.mkdir(parents=True, exist_ok=True)
            if create_venv is None:
                venv.EnvBuilder(with_pip=True, system_site_packages=True).create(venv_full)
            else:
                create_venv(venv_full)
            python = _venv_python(venv_full)
            install_result = runner([str(python), "-m", "pip", "install", "--no-index", "--find-links", str(wheel.parent), str(wheel)], 300, root)
            import_result = runner([str(python), "-c", "import ai_objective_index; print(ai_objective_index.__name__)"], 120, root)
            smoke_result = runner([str(python), "-m", "ai_objective_index.mcp_smoke"], 120, root)
            vnext_smoke_result = runner(
                [
                    str(python),
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
                180,
                root,
            )
            probe_smoke_result = runner(
                [
                    str(python),
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
                180,
                root,
            )
            script = venv_full / ("Scripts/ai-objective-index-mcp-smoke.exe" if sys.platform == "win32" else "bin/ai-objective-index-mcp-smoke")
            if script.exists():
                console_smoke_result = runner([str(script)], 120, root)
            else:
                warnings.append("Console smoke script was not found in the temp venv.")
            decision = (
                "PASS_LOCAL_INSTALL_SMOKE"
                if install_result.get("ok")
                and import_result.get("ok")
                and smoke_result.get("ok")
                and vnext_smoke_result.get("ok")
                and probe_smoke_result.get("ok")
                else "HOLD_LOCAL_INSTALL_SMOKE_FAILED"
            )
            if decision != "PASS_LOCAL_INSTALL_SMOKE":
                errors.append("Local install smoke did not fully pass.")
        except Exception as exc:
            decision = "HOLD_LOCAL_INSTALL_SMOKE_FAILED"
            errors.append(_sanitize(exc))
        finally:
            if cleanup and venv_full.exists():
                shutil.rmtree(venv_full, ignore_errors=True)

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "wheel_path": str(wheel.relative_to(root)) if wheel else "",
        "venv_path": str(venv_full),
        "venv_cleaned": cleanup,
        "install_result": install_result,
        "import_result": import_result,
        "mcp_smoke_result": smoke_result,
        "vnext_objective_router_smoke_result": vnext_smoke_result,
        "vnext_probe_smoke_result": probe_smoke_result,
        "console_smoke_result": console_smoke_result,
        "errors": errors,
        "warnings": warnings,
        "network_required": False,
        "upload_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_local_install_smoke()
    print(
        "local_install_smoke: "
        f"{result['decision']} "
        f"wheel={result['wheel_path']} "
        "upload_performed=False"
    )


if __name__ == "__main__":
    main()
