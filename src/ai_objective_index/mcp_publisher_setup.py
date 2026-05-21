from __future__ import annotations

import json
import shutil
import subprocess
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "wave11_mcp_registry" / "MCP_PUBLISHER_SETUP_RESULT.json"
OFFICIAL_RELEASE_HOST = "github.com/modelcontextprotocol/registry"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _redact(text: Any) -> str:
    value = str(text or "")
    for marker in ["ghp_", "gho_", "github_pat_", "pypi-", "hf_"]:
        value = value.replace(marker, f"{marker}[redacted]")
    return value[:2000]


def _publisher_help(path: str) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [path, "--help"],
            cwd=_repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": _redact(exc)}
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": _redact(completed.stdout),
        "stderr": _redact(completed.stderr),
    }


def _instructions() -> list[str]:
    return [
        "Install mcp-publisher from the official modelcontextprotocol/registry GitHub releases.",
        "Put the binary on PATH as mcp-publisher or run from its installed directory.",
        "Run: python -m ai_objective_index.mcp_publisher_setup --check",
        "Then run: python -m ai_objective_index.mcp_registry_publish_runner --login",
        "Do not paste GitHub tokens into chat and do not commit credentials.",
    ]


def run_mcp_publisher_setup(
    mode: str = "check",
    download_url: str | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    warnings: list[str] = []
    errors: list[str] = []
    path = shutil.which("mcp-publisher")
    help_result: dict[str, Any] = {}
    download_attempted = False

    if mode == "download-windows":
        download_attempted = True
        if download_url and OFFICIAL_RELEASE_HOST not in download_url:
            decision = "BLOCK_UNSAFE_BINARY_SOURCE"
            errors.append("Download source is not the official modelcontextprotocol/registry GitHub release host.")
        else:
            decision = "HOLD_MANUAL_INSTALL_REQUIRED"
            warnings.append("Automatic binary download is intentionally not performed; use manual install instructions.")
    elif path:
        help_result = _publisher_help(path)
        if help_result.get("ok"):
            decision = "PASS_MCP_PUBLISHER_AVAILABLE"
        else:
            decision = "HOLD_MCP_PUBLISHER_MISSING"
            warnings.append("mcp-publisher is on PATH but --help did not exit cleanly.")
    elif mode == "install-instructions":
        decision = "HOLD_MANUAL_INSTALL_REQUIRED"
        warnings.append("Manual mcp-publisher installation is required.")
    else:
        decision = "HOLD_MCP_PUBLISHER_MISSING"
        warnings.append("mcp-publisher is not available on PATH.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "decision": decision,
        "mcp_publisher_available": bool(path),
        "mcp_publisher_path": path or "",
        "help_result": help_result,
        "download_attempted": download_attempted,
        "download_performed": False,
        "token_printed": False,
        "instructions": _instructions(),
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--install-instructions", action="store_true")
    group.add_argument("--download-windows", action="store_true")
    args = parser.parse_args()
    mode = "check"
    if args.install_instructions:
        mode = "install-instructions"
    elif args.download_windows:
        mode = "download-windows"
    result = run_mcp_publisher_setup(mode=mode)
    print(f"mcp_publisher_setup: {result['decision']} available={result['mcp_publisher_available']}")


if __name__ == "__main__":
    main()
