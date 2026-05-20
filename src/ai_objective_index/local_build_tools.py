from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable


WAVE3_DIR = Path("public_launch") / "wave3"
OUTPUT_PATH = WAVE3_DIR / "LOCAL_BUILD_TOOLS_RESULT.json"


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
    return text[:1200]


def _run(command: list[str], timeout: int = 300) -> dict[str, Any]:
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


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def run_local_build_tools(
    install: bool = False,
    runner: Callable[[list[str], int], dict[str, Any]] = _run,
    write_result: bool = True,
) -> dict[str, Any]:
    build_before = module_available("build")
    twine_before = module_available("twine")
    setuptools_before = module_available("setuptools")
    install_result: dict[str, Any] = {"ok": False, "skipped": True}
    errors: list[str] = []
    warnings: list[str] = []

    if install:
        install_result = runner([sys.executable, "-m", "pip", "install", "--upgrade", "build", "twine", "setuptools"], 600)
        if not install_result.get("ok"):
            errors.append("Failed to install or upgrade build/twine/setuptools.")
    elif not build_before or not twine_before:
        warnings.append("One or more local packaging tools are missing. Run with --install if local installation is desired.")

    build_after = module_available("build")
    twine_after = module_available("twine")
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "build_available_before": build_before,
        "twine_available_before": twine_before,
        "install_attempted": install,
        "setuptools_available_before": setuptools_before,
        "install_result": install_result,
        "build_available_after": build_after,
        "twine_available_after": twine_after,
        "setuptools_available_after": module_available("setuptools"),
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


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Check or install local PyPI packaging tools for AOI.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args(argv)
    result = run_local_build_tools(install=bool(args.install))
    print(
        "local_build_tools: "
        f"install_attempted={result['install_attempted']} "
        f"build={result['build_available_after']} "
        f"twine={result['twine_available_after']} "
        f"errors={len(result['errors'])}"
    )


if __name__ == "__main__":
    main()
