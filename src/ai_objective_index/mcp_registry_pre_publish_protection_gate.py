from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .anti_clone_risk_audit import OUTPUT_PATH as CLONE_PATH, run_anti_clone_risk_audit
from .license_ip_positioning_audit import OUTPUT_PATH as LICENSE_PATH, run_license_ip_positioning_audit
from .mcp_registry_manifest_final_audit import OUTPUT_PATH as MANIFEST_PATH, run_mcp_registry_manifest_final_audit
from .package_artifact_exposure_audit import OUTPUT_PATH as ARTIFACT_PATH, run_package_artifact_exposure_audit
from .public_private_split_audit import OUTPUT_PATH as SPLIT_PATH, run_public_private_split_audit
from .real_pypi_upload_gate import _repo_root
from .tech_protection_audit import OUTPUT_PATH as TECH_PATH, run_tech_protection_audit


OUTPUT_PATH = Path("public_launch") / "wave12_tech_protection" / "MCP_REGISTRY_PRE_PUBLISH_PROTECTION_GATE.json"
NEXT_PATH = Path("public_launch") / "wave12_tech_protection" / "NEXT_MCP_REGISTRY_AFTER_PROTECTION.md"
SUMMARY_PATH = Path("public_launch") / "wave12_tech_protection" / "TECHNOLOGY_PROTECTION_SUMMARY.md"
SPLIT_SUMMARY_PATH = Path("public_launch") / "wave12_tech_protection" / "PUBLIC_PRIVATE_SPLIT_SUMMARY.md"


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


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


def run_mcp_registry_pre_publish_protection_gate(write_result: bool = True) -> dict[str, Any]:
    tech = _read_json(TECH_PATH) or run_tech_protection_audit(write_result=False)
    split = _read_json(SPLIT_PATH) or run_public_private_split_audit(write_result=False)
    artifact = _read_json(ARTIFACT_PATH) or run_package_artifact_exposure_audit(write_result=False)
    clone = _read_json(CLONE_PATH) or run_anti_clone_risk_audit(write_result=False)
    license_result = _read_json(LICENSE_PATH) or run_license_ip_positioning_audit(write_result=False)
    manifest = _read_json(MANIFEST_PATH) or run_mcp_registry_manifest_final_audit(write_result=False)
    warnings: list[str] = []
    errors: list[str] = []

    if not _no_secret_real_findings():
        decision = "BLOCK_SECRET_OR_PRIVATE_KERNEL_EXPOSED"
        errors.append("no_secrets_audit reports real findings.")
    elif not _claim_guard_passed():
        decision = "BLOCK_OVERCLAIM"
        errors.append("launch_claim_guard is not PASS.")
    elif str(tech.get("decision", "")).startswith("BLOCK"):
        decision = "BLOCK_SECRET_OR_PRIVATE_KERNEL_EXPOSED"
        errors.append("Technology protection audit found a blocking exposure.")
    elif artifact.get("decision") == "BLOCK_SENSITIVE_ARTIFACT_IN_PACKAGE":
        decision = "BLOCK_PACKAGE_ARTIFACT_SENSITIVE"
        errors.append("Package artifact exposure audit found a sensitive artifact.")
    elif manifest.get("decision") == "BLOCK_OVERCLAIM":
        decision = "BLOCK_OVERCLAIM"
        errors.append("Manifest final audit found overclaim wording.")
    elif license_result.get("decision") in {"HOLD_LICENSE_REVIEW_RECOMMENDED", "BLOCK_LICENSE_MISSING_FOR_PUBLIC_REPO"}:
        decision = "HOLD_LICENSE_REVIEW" if not str(license_result.get("decision")).startswith("BLOCK") else "BLOCK_SECRET_OR_PRIVATE_KERNEL_EXPOSED"
        warnings.append("License/IP positioning should be reviewed before Registry publish.")
    elif split.get("decision") != "PASS_PUBLIC_PRIVATE_SPLIT_CLEAR":
        decision = "HOLD_PRIVATE_SPLIT_REVIEW"
        warnings.append("Public/private split is not fully clear.")
    elif clone.get("decision") != "PASS_ACCEPTABLE_PUBLIC_BETA_RISK":
        decision = "HOLD_CLONE_RISK_REVIEW"
        warnings.append("Clone-risk posture should be reviewed.")
    elif artifact.get("decision") != "PASS_PACKAGE_ARTIFACT_SAFE":
        decision = "HOLD_PRIVATE_SPLIT_REVIEW"
        warnings.append("Package artifacts need review before Registry publish.")
    elif manifest.get("decision") != "PASS_MANIFEST_READY":
        decision = "HOLD_PRIVATE_SPLIT_REVIEW"
        warnings.append("MCP Registry manifest is not ready.")
    else:
        decision = "PASS_READY_FOR_MCP_REGISTRY_AFTER_PROTECTION"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "tech_protection_decision": tech.get("decision"),
        "public_private_split_decision": split.get("decision"),
        "package_artifact_decision": artifact.get("decision"),
        "anti_clone_risk_decision": clone.get("decision"),
        "anti_clone_risk_level": clone.get("risk_level"),
        "license_ip_decision": license_result.get("decision"),
        "manifest_final_audit_decision": manifest.get("decision"),
        "recommended_next_package": "8R-B MCP Publisher Install + Registry Submit" if decision == "PASS_READY_FOR_MCP_REGISTRY_AFTER_PROTECTION" else "Package 8S remediation before MCP Registry publish",
        "mcp_registry_submission_performed": False,
        "token_printed": False,
        "errors": errors,
        "warnings": warnings,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
        _write(
            SUMMARY_PATH,
            f"""# Technology Protection Summary

- Technology protection audit: `{tech.get('decision')}`
- Public/private split audit: `{split.get('decision')}`
- Package artifact exposure audit: `{artifact.get('decision')}`
- Anti-clone risk audit: `{clone.get('decision')}` / `{clone.get('risk_level')}`
- License/IP positioning audit: `{license_result.get('decision')}`
- Pre-publish protection gate: `{decision}`

AOI public surfaces may expose schemas, API/MCP shapes, source-trace discipline, route labels, limitations, and sample data. Private weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, and commercial routing policy remain non-public.
""",
        )
        _write(
            SPLIT_SUMMARY_PATH,
            """# Public/Private Split Summary

Public: schemas, endpoint shapes, MCP tool descriptions, high-level components, source-trace methodology, ALLOW/HOLD/BLOCK labels, limitations, and sample public data.

Private: exact weights, thresholds, anti-gaming heuristics, provider trust priors, private negative controls, private probe seeds, receipt weighting logic, commercial routing policy, and private data strategy.
""",
        )
        _write(
            NEXT_PATH,
            f"""# Next MCP Registry Step After Protection

Current gate: `{decision}`

If the gate is `PASS_READY_FOR_MCP_REGISTRY_AFTER_PROTECTION`, the next package can be 8R-B MCP Publisher Install + Registry Submit.

If the gate is HOLD or BLOCK, resolve the listed findings first. Do not submit MCP Registry metadata, install/execute `mcp-publisher`, upload a new PyPI version, or expose private kernel details from this package.
""",
        )
    return result


def main() -> None:
    result = run_mcp_registry_pre_publish_protection_gate()
    print(f"mcp_registry_pre_publish_protection_gate: {result['decision']}")


if __name__ == "__main__":
    main()
