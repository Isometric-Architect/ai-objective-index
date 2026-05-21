from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .mcp_publisher_auth_check import OUTPUT_PATH as AUTH_PATH, run_mcp_publisher_auth_check
from .mcp_publisher_installer import OUTPUT_PATH as INSTALL_PATH, find_mcp_publisher, run_mcp_publisher_installer
from .mcp_registry_manifest_final_audit import OUTPUT_PATH as MANIFEST_PATH, run_mcp_registry_manifest_final_audit
from .mcp_registry_pre_publish_protection_gate import OUTPUT_PATH as PROTECTION_PATH, run_mcp_registry_pre_publish_protection_gate
from .real_pypi_release_audit import OUTPUT_PATH as PYPI_AUDIT_PATH
from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "wave13_mcp_registry_submit" / "MCP_REGISTRY_PUBLISH_PREFLIGHT.json"


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


def _claim_guard_passed() -> bool:
    path = _repo_root() / "data" / "generated" / "launch_claim_guard_result_v0_2.json"
    if not path.exists():
        return True
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return payload.get("overall_token") == "PASS" or payload.get("risky_phrase_count") == 0


def _no_secret_real_findings() -> bool:
    path = _repo_root() / "data" / "generated" / "no_secrets_audit_result_v0_2.json"
    if not path.exists():
        return True
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return int(payload.get("finding_count", payload.get("findings", 0)) or 0) == 0


def _auth_passed(auth: dict[str, Any]) -> bool:
    return auth.get("decision") == "PASS_AUTH_CONFIRMED" or (auth.get("login_attempted") and (auth.get("login_result") or {}).get("ok"))


def run_mcp_registry_publish_preflight(write_result: bool = True) -> dict[str, Any]:
    install = _read_json(INSTALL_PATH) or run_mcp_publisher_installer(write_result=False)
    auth = _read_json(AUTH_PATH)
    if not auth and find_mcp_publisher():
        auth = run_mcp_publisher_auth_check(write_result=False)
    manifest = _read_json(MANIFEST_PATH) or run_mcp_registry_manifest_final_audit(write_result=False)
    protection = _read_json(PROTECTION_PATH) or run_mcp_registry_pre_publish_protection_gate(write_result=False)
    pypi = _read_json(PYPI_AUDIT_PATH)
    publisher_available = bool(find_mcp_publisher()) or install.get("decision") in {"PASS_MCP_PUBLISHER_AVAILABLE", "PASS_MCP_PUBLISHER_DOWNLOADED_LOCAL"}
    warnings: list[str] = []
    errors: list[str] = []

    if not _no_secret_real_findings():
        decision = "BLOCK_SECRET_FINDING"
        errors.append("no_secrets_audit reports real findings.")
    elif not _claim_guard_passed():
        decision = "BLOCK_OVERCLAIM"
        errors.append("launch_claim_guard is not PASS.")
    elif manifest.get("decision") != "PASS_MANIFEST_READY":
        decision = "BLOCK_MANIFEST_MISMATCH"
        errors.append("Manifest final audit is not PASS.")
    elif pypi.get("decision") != "PASS_REAL_PYPI_RELEASE_VERIFIED":
        decision = "HOLD_PYPI_NOT_VERIFIED"
        warnings.append("Real PyPI release audit has not passed.")
    elif protection.get("decision") != "PASS_READY_FOR_MCP_REGISTRY_AFTER_PROTECTION":
        decision = "HOLD_PROTECTION_GATE_NOT_PASS"
        warnings.append("Package 8S protection gate is not PASS.")
    elif not publisher_available:
        decision = "HOLD_MCP_PUBLISHER_MISSING"
        warnings.append("mcp-publisher is not available.")
    elif auth.get("decision") == "HOLD_AUTH_STATUS_NOT_CHECKED":
        decision = "HOLD_AUTH_STATUS_NOT_CHECKED"
        warnings.append("Authentication status has not been confirmed; run mcp_publisher_auth_check --login.")
    elif not _auth_passed(auth):
        decision = "HOLD_LOGIN_REQUIRED"
        warnings.append("mcp-publisher GitHub login is required before submit.")
    else:
        decision = "PASS_READY_TO_SUBMIT"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "publisher_install_decision": install.get("decision"),
        "publisher_auth_decision": auth.get("decision"),
        "manifest_final_audit_decision": manifest.get("decision"),
        "protection_gate_decision": protection.get("decision"),
        "pypi_release_audit_decision": pypi.get("decision"),
        "mcp_publisher_available": publisher_available,
        "token_printed": False,
        "mcp_registry_submission_performed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_mcp_registry_publish_preflight()
    print(f"mcp_registry_publish_preflight: {result['decision']}")


if __name__ == "__main__":
    main()
