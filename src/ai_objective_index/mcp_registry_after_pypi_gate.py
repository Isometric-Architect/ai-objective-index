from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .package_metadata_audit import MCP_MARKER, MCP_NAME
from .real_pypi_install_verify import OUTPUT_PATH as INSTALL_RESULT_PATH
from .real_pypi_upload_gate import PACKAGE_NAME, TARGET_VERSION, _repo_root, tracked_token_findings
from .real_pypi_upload_runner import OUTPUT_PATH as UPLOAD_RESULT_PATH


OUTPUT_PATH = Path("public_launch") / "wave10_real_pypi" / "MCP_REGISTRY_AFTER_PYPI_GATE_RESULT.json"


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


def _read(path: str) -> str:
    full = _repo_root() / path
    return full.read_text(encoding="utf-8", errors="ignore") if full.exists() else ""


def _read_server_json() -> dict[str, Any]:
    return _read_json(Path(".mcp") / "server.json")


def _claim_guard_passed() -> bool:
    path = _repo_root() / "data" / "generated" / "launch_claim_guard_result_v0_2.json"
    if not path.exists():
        return True
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return payload.get("overall_token") == "PASS" or payload.get("risky_phrase_count") == 0


def run_mcp_registry_after_pypi_gate(write_result: bool = True) -> dict[str, Any]:
    upload = _read_json(UPLOAD_RESULT_PATH)
    install = _read_json(INSTALL_RESULT_PATH)
    server = _read_server_json()
    packages = server.get("packages", []) if isinstance(server.get("packages"), list) else []
    package = packages[0] if packages and isinstance(packages[0], dict) else {}
    readme = _read("README.md")
    token_findings = tracked_token_findings()
    mcp_publisher_path = shutil.which("mcp-publisher")
    errors: list[str] = []
    warnings: list[str] = []

    upload_confirmed = upload.get("result_token") in {"UPLOAD_SUCCESS", "HOLD_ALREADY_EXISTS"}
    install_passed = install.get("decision") == "PASS_REAL_PYPI_INSTALL"
    metadata_ok = (
        server.get("name") == MCP_NAME
        and MCP_MARKER in readme
        and server.get("version") == TARGET_VERSION
        and package.get("registryType") == "pypi"
        and package.get("identifier") == PACKAGE_NAME
        and package.get("version") == TARGET_VERSION
    )
    if token_findings:
        decision = "BLOCK_SECRET_FINDING"
        errors.append("Tracked token-like content found.")
    elif not _claim_guard_passed():
        decision = "BLOCK_OVERCLAIM"
        errors.append("Launch claim guard output is not PASS.")
    elif not metadata_ok:
        decision = "BLOCK_METADATA_MISMATCH"
        errors.append("server.json / README PyPI registry metadata mismatch.")
    elif not upload_confirmed:
        decision = "HOLD_PYPI_UPLOAD_FIRST"
        warnings.append("Real PyPI upload has not been confirmed.")
    elif not install_passed:
        decision = "HOLD_REAL_PYPI_INSTALL_VERIFY_FIRST"
        warnings.append("Real PyPI install verification has not passed.")
    elif not mcp_publisher_path:
        decision = "HOLD_MCP_PUBLISHER_REQUIRED"
        warnings.append("Install or locate mcp-publisher before registry dry-run.")
    else:
        decision = "PASS_READY_FOR_MCP_REGISTRY_DRY_RUN"
        warnings.append("Registry auth and explicit publish confirmation are still required before submission.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "server_name": server.get("name"),
        "server_version": server.get("version"),
        "registry_type": package.get("registryType"),
        "identifier": package.get("identifier"),
        "package_version": package.get("version"),
        "readme_marker_matches": server.get("name") == MCP_NAME and MCP_MARKER in readme,
        "real_pypi_upload_result": upload.get("result_token"),
        "real_pypi_install_verify": install.get("decision"),
        "mcp_publisher_available": bool(mcp_publisher_path),
        "mcp_publisher_path": mcp_publisher_path or "",
        "mcp_registry_submission_performed": False,
        "testpypi_used": False,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_mcp_registry_after_pypi_gate()
    print(
        "mcp_registry_after_pypi_gate: "
        f"{result['decision']} "
        "submission_performed=False"
    )


if __name__ == "__main__":
    main()
