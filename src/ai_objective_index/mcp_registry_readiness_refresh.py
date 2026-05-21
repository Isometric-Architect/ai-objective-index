from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .package_metadata_audit import MCP_MARKER, MCP_NAME


TARGET_VERSION = "0.3.0a1"
OUTPUT_PATH = Path("public_launch") / "wave9" / "MCP_REGISTRY_READINESS_REFRESH_RESULT.json"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _read_json(path: str | Path) -> dict[str, Any]:
    full = Path(path)
    if not full.is_absolute():
        full = _repo_root() / full
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _read(path: str) -> str:
    full = _repo_root() / path
    return full.read_text(encoding="utf-8", errors="ignore") if full.exists() else ""


def run_mcp_registry_readiness_refresh(write_result: bool = True) -> dict[str, Any]:
    server = _read_json(Path(".mcp") / "server.json")
    pypi = _read_json(Path("public_launch") / "wave9" / "PYPI_READINESS_REFRESH_RESULT.json")
    build = _read_json(Path("public_launch") / "wave9" / "DIST_BUILD_RESULT.json")
    readme = _read("README.md")
    packages = server.get("packages", []) if isinstance(server.get("packages"), list) else []
    package = packages[0] if packages and isinstance(packages[0], dict) else {}
    errors: list[str] = []
    warnings: list[str] = []

    if server.get("name") != MCP_NAME or MCP_MARKER not in readme:
        errors.append("README mcp-name marker and server.json name do not match.")
    if package.get("registryType") != "pypi":
        errors.append("server.json package registryType is not pypi.")
    if package.get("identifier") != "ai-objective-index":
        errors.append("server.json package identifier is not ai-objective-index.")
    if server.get("version") != TARGET_VERSION or package.get("version") != TARGET_VERSION:
        errors.append("server.json version does not match 0.3.0a1.")
    if build.get("decision") != "PASS_BUILD_READY":
        warnings.append("Package build is not marked PASS_BUILD_READY.")

    pypi_uploaded = bool(pypi.get("pypi_upload_performed") or pypi.get("pypi_uploaded"))
    testpypi_uploaded = bool(pypi.get("testpypi_upload_performed"))
    if errors:
        decision = "BLOCK_VERSION_MISMATCH" if any("version" in error.lower() for error in errors) else "BLOCK_METADATA_MISMATCH"
    elif not testpypi_uploaded:
        decision = "HOLD_TESTPYPI_FIRST"
        warnings.append("Run TestPyPI upload and install verification before PyPI/MCP Registry submission.")
    elif not pypi_uploaded:
        decision = "HOLD_PYPI_UPLOAD_REQUIRED"
        warnings.append("PyPI package has not been uploaded or verified.")
    else:
        decision = "HOLD_MCP_PUBLISHER_AND_AUTH_REQUIRED"
        warnings.append("PyPI appears uploaded, but MCP publisher/auth checks are still required.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "server_name": server.get("name"),
        "server_version": server.get("version"),
        "registry_type": package.get("registryType"),
        "identifier": package.get("identifier"),
        "package_version": package.get("version"),
        "readme_marker_matches": server.get("name") == MCP_NAME and MCP_MARKER in readme,
        "package_build_decision": build.get("decision"),
        "pypi_readiness_decision": pypi.get("decision"),
        "testpypi_upload_performed": testpypi_uploaded,
        "pypi_upload_performed": pypi_uploaded,
        "mcp_registry_submission_performed": False,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_mcp_registry_readiness_refresh()
    print(
        "mcp_registry_readiness_refresh: "
        f"{result['decision']} "
        f"version={result['server_version']} "
        "submission_performed=False"
    )


if __name__ == "__main__":
    main()
