from __future__ import annotations

import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .mcp_registry_pypi_builder import SERVER_JSON_PATH, write_pypi_server_json
from .package_metadata_audit import MCP_MARKER, MCP_NAME, run_package_metadata_audit


WAVE2_DIR = Path("public_launch") / "wave2"
OUTPUT_PATH = WAVE2_DIR / "MCP_REGISTRY_PUBLISH_READINESS_RESULT.json"


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


def _dist_exists() -> bool:
    dist = _repo_root() / "dist"
    return dist.exists() and any(dist.glob("ai_objective_index-0.2.0*"))


def _pypi_uploaded_known() -> bool:
    marker = _read_json("public_launch/wave2/PYPI_UPLOAD_STATUS.json")
    return bool(marker.get("pypi_uploaded"))


def _server_json() -> dict[str, Any]:
    if not (_repo_root() / SERVER_JSON_PATH).exists():
        write_pypi_server_json()
    return _read_json(SERVER_JSON_PATH)


def _server_name_valid(name: str) -> bool:
    return bool(re.fullmatch(r"io\.github\.[a-z0-9][a-z0-9-]*/[a-z0-9][a-z0-9-]*", name))


def run_mcp_registry_publish_readiness(
    pypi_uploaded: bool | None = None,
    mcp_publisher_available: bool | None = None,
    registry_auth_available: bool | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    metadata = run_package_metadata_audit(write_result=True)
    server = _server_json()
    pypi_readiness = _read_json("public_launch/wave2/PYPI_PUBLISH_READINESS_RESULT.json")
    pypi_uploaded = _pypi_uploaded_known() if pypi_uploaded is None else pypi_uploaded
    mcp_publisher_available = shutil.which("mcp-publisher") is not None if mcp_publisher_available is None else mcp_publisher_available
    registry_auth_available = False if registry_auth_available is None else registry_auth_available

    errors: list[str] = []
    holds: list[str] = []
    server_name = str(server.get("name") or "")
    readme = _read("README.md")
    if server_name != MCP_NAME or MCP_MARKER not in readme:
        decision = "BLOCK_METADATA_MISMATCH"
        errors.append("README mcp-name marker and server.json name do not match.")
    elif not _server_name_valid(server_name):
        decision = "BLOCK_METADATA_MISMATCH"
        errors.append("server.json name is not a valid registry namespace.")
    elif metadata.get("overall_token") != "PASS":
        decision = "BLOCK_OVERCLAIM"
        errors.append("package metadata audit did not pass.")
    else:
        build_decision = pypi_readiness.get("decision", "missing")
        build_ready = build_decision in {"PASS_BUILD_READY", "HOLD_TWINE_MISSING", "HOLD_LOCAL_INSTALL_NOT_CHECKED"} and (_dist_exists() or bool(pypi_readiness.get("dist_files")))
        if not build_ready:
            decision = "HOLD_BUILD_NOT_READY"
            holds.append("Build readiness is not complete or dist files are missing.")
        elif not pypi_uploaded:
            decision = "HOLD_PYPI_UPLOAD_REQUIRED"
            holds.append("PyPI package has not been uploaded or verified.")
        elif not mcp_publisher_available:
            decision = "HOLD_MCP_PUBLISHER_MISSING"
            holds.append("mcp-publisher CLI is unavailable.")
        elif not registry_auth_available:
            decision = "HOLD_AUTH_MISSING"
            holds.append("MCP Registry authentication is not available.")
        else:
            decision = "PASS_READY_TO_SUBMIT"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "server_json_exists": (_repo_root() / SERVER_JSON_PATH).exists(),
        "server_name": server_name,
        "readme_marker": MCP_MARKER in readme,
        "package_metadata_token": metadata.get("overall_token"),
        "pypi_build_decision": pypi_readiness.get("decision", "missing"),
        "pypi_uploaded": pypi_uploaded,
        "mcp_publisher_available": mcp_publisher_available,
        "registry_auth_available": registry_auth_available,
        "errors": errors,
        "holds": holds,
        "submission_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_mcp_registry_publish_readiness()
    print(
        "mcp_registry_publish_readiness: "
        f"{result['decision']} "
        f"pypi_uploaded={result['pypi_uploaded']} "
        "submission_performed=False"
    )


if __name__ == "__main__":
    main()
