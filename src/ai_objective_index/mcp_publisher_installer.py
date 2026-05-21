from __future__ import annotations

import json
import os
import shutil
import subprocess
import tarfile
import urllib.error
import urllib.request
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "wave13_mcp_registry_submit" / "MCP_PUBLISHER_INSTALL_RESULT.json"
TOOLS_DIR = Path("tools") / "mcp-publisher"
WINDOWS_ASSET_NAME = "mcp-publisher_windows_amd64.tar.gz"
LATEST_RELEASE_API = "https://api.github.com/repos/modelcontextprotocol/registry/releases/latest"
DOWNLOAD_CONFIRM_ENV = "AOI_MCP_PUBLISHER_DOWNLOAD_CONFIRM"


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def redact_token_like(text: Any) -> str:
    value = str(text or "")
    for marker in ["github_pat_", "ghp_", "gho_", "ghu_", "ghs_", "Bearer ", "pypi-", "hf_"]:
        value = value.replace(marker, f"{marker}[redacted]")
    return value[:4000]


def local_publisher_path() -> Path:
    return _repo_root() / TOOLS_DIR / "mcp-publisher.exe"


def find_mcp_publisher() -> str:
    local = local_publisher_path()
    if local.exists():
        return str(local)
    for name in ["mcp-publisher", "mcp-publisher.exe"]:
        found = shutil.which(name)
        if found:
            return found
    return ""


def run_publisher_help(command: str) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [command, "--help"],
            cwd=_repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError) as exc:
        return {"ok": False, "returncode": None, "stdout": "", "stderr": redact_token_like(exc)}
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": redact_token_like(completed.stdout),
        "stderr": redact_token_like(completed.stderr),
    }


def _instructions() -> list[str]:
    return [
        "Download mcp-publisher from the official modelcontextprotocol/registry GitHub releases.",
        f"Expected Windows x64 asset: {WINDOWS_ASSET_NAME}",
        "Extract mcp-publisher.exe into tools/mcp-publisher/ or another local folder.",
        "Run: python -m ai_objective_index.mcp_publisher_installer --check",
        "Authenticate with: python -m ai_objective_index.mcp_publisher_auth_check --login",
        "Do not paste GitHub tokens into chat and do not commit downloaded credentials.",
    ]


def _safe_asset_url(url: str) -> bool:
    return (
        url.startswith("https://github.com/modelcontextprotocol/registry/releases/download/")
        and url.endswith(f"/{WINDOWS_ASSET_NAME}")
    )


def _resolve_windows_asset_url() -> str:
    request = urllib.request.Request(LATEST_RELEASE_API, headers={"User-Agent": "ai-objective-index-mcp-publisher-installer"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    for asset in payload.get("assets", []):
        if asset.get("name") == WINDOWS_ASSET_NAME:
            url = str(asset.get("browser_download_url") or "")
            if not _safe_asset_url(url):
                raise ValueError("Unsafe mcp-publisher asset URL.")
            return url
    raise FileNotFoundError(f"{WINDOWS_ASSET_NAME} not found in latest release assets.")


def _extract_expected_binary(archive_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:gz") as archive:
        expected_members = [
            member
            for member in archive.getmembers()
            if member.isfile() and Path(member.name).name.lower() in {"mcp-publisher.exe", "mcp-publisher"}
        ]
        if not expected_members:
            raise FileNotFoundError("Expected mcp-publisher binary was not present in archive.")
        member = expected_members[0]
        target = output_dir / ("mcp-publisher.exe" if Path(member.name).suffix.lower() == ".exe" else "mcp-publisher")
        source = archive.extractfile(member)
        if source is None:
            raise OSError("Could not read mcp-publisher binary from archive.")
        target.write_bytes(source.read())
    return target


def _download_windows_asset(asset_url: str | None = None) -> Path:
    url = asset_url or _resolve_windows_asset_url()
    if not _safe_asset_url(url):
        raise ValueError("Unsafe mcp-publisher asset URL.")
    output_dir = _repo_root() / TOOLS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / WINDOWS_ASSET_NAME
    request = urllib.request.Request(url, headers={"User-Agent": "ai-objective-index-mcp-publisher-installer"})
    with urllib.request.urlopen(request, timeout=120) as response:
        archive_path.write_bytes(response.read())
    binary = _extract_expected_binary(archive_path, output_dir)
    try:
        archive_path.unlink()
    except OSError:
        pass
    return binary


def run_mcp_publisher_installer(
    mode: str = "check",
    env: dict[str, str] | None = None,
    asset_url: str | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    errors: list[str] = []
    warnings: list[str] = []
    path = find_mcp_publisher()
    help_result: dict[str, Any] = {}
    downloaded_path = ""

    if mode == "instructions":
        decision = "HOLD_MANUAL_INSTALL_REQUIRED"
        warnings.append("Manual mcp-publisher installation instructions written.")
    elif mode == "download-windows":
        if env_map.get(DOWNLOAD_CONFIRM_ENV) != "YES":
            decision = "HOLD_MANUAL_INSTALL_REQUIRED"
            warnings.append(f"{DOWNLOAD_CONFIRM_ENV}=YES is required before downloading mcp-publisher.")
        elif asset_url and not _safe_asset_url(asset_url):
            decision = "BLOCK_UNSAFE_BINARY_SOURCE"
            errors.append("Asset URL is not the expected official modelcontextprotocol/registry release asset.")
        else:
            try:
                binary = _download_windows_asset(asset_url=asset_url)
                downloaded_path = str(binary)
                help_result = run_publisher_help(str(binary))
                decision = "PASS_MCP_PUBLISHER_DOWNLOADED_LOCAL" if help_result.get("ok") else "BLOCK_DOWNLOAD_FAILED"
                if not help_result.get("ok"):
                    errors.append("Downloaded mcp-publisher did not run --help successfully.")
            except (OSError, ValueError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, tarfile.TarError) as exc:
                decision = "BLOCK_DOWNLOAD_FAILED"
                errors.append(redact_token_like(exc))
    elif path:
        help_result = run_publisher_help(path)
        decision = "PASS_MCP_PUBLISHER_AVAILABLE" if help_result.get("ok") else "HOLD_MCP_PUBLISHER_MISSING"
        if not help_result.get("ok"):
            warnings.append("mcp-publisher was found but --help did not complete successfully.")
    else:
        decision = "HOLD_MCP_PUBLISHER_MISSING"
        warnings.append("mcp-publisher is not available on PATH or tools/mcp-publisher/.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "decision": decision,
        "mcp_publisher_available": decision in {"PASS_MCP_PUBLISHER_AVAILABLE", "PASS_MCP_PUBLISHER_DOWNLOADED_LOCAL"},
        "mcp_publisher_path": downloaded_path or path,
        "download_attempted": mode == "download-windows",
        "download_performed": bool(downloaded_path),
        "help_result": help_result,
        "instructions": _instructions(),
        "token_printed": False,
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
    group.add_argument("--instructions", action="store_true")
    group.add_argument("--download-windows", action="store_true")
    args = parser.parse_args()
    mode = "check"
    if args.instructions:
        mode = "instructions"
    elif args.download_windows:
        mode = "download-windows"
    result = run_mcp_publisher_installer(mode=mode)
    print(f"mcp_publisher_installer: {result['decision']} available={result['mcp_publisher_available']}")


if __name__ == "__main__":
    main()
