from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .launch_claim_guard import run_launch_claim_guard
from .no_secrets_audit import run_no_secrets_audit, save_no_secrets_audit
from .residualops_alignment_audit import run_residualops_alignment_audit
from .smoke_all import run_smoke_all
from .vnext_capability_trust_audit import run_capability_trust_claim_audit
from .vnext_execution_receipt_audit import run_execution_receipt_claim_audit
from .vnext_objective_router_audit import run_objective_router_claim_audit
from .vnext_package_version_audit import run_vnext_package_version_audit
from .vnext_probe_audit import run_probe_claim_audit
from .vnext_surface_sync_audit import run_vnext_surface_sync_audit


OUTPUT_PATH = Path("public_launch") / "wave8" / "VNEXT_DISTRIBUTION_GATE_RESULT.json"
SUMMARY_PATH = Path("public_launch") / "wave8" / "VNEXT_DISTRIBUTION_SUMMARY.md"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_summary(result: dict[str, Any]) -> None:
    text = f"""# vNext Distribution Summary

- Distribution gate decision: `{result['decision']}`
- Surface sync: `{result['checks']['surface_sync']}`
- Version audit: `{result['checks']['version_audit']}`
- ResidualOps alignment: `{result['checks']['residualops_alignment']}`
- vNext claim audits: `{result['checks']['vnext_claim_audits']}`
- no_secrets: `{result['checks']['no_secrets']}`
- launch_claim_guard: `{result['checks']['launch_claim_guard']}`
- smoke_all: `{result['checks']['smoke_all']}`

Package 9F does not upload to PyPI/TestPyPI, submit MCP Registry metadata, post to communities, execute external tools, call live MCP servers, fetch URLs, or request tokens.

Next recommended package: Resume 8Q-A Local Build Tool Install + Dist Build + Twine Check after the version decision is made.
"""
    destination = _repo_root() / SUMMARY_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def run_vnext_distribution_gate(write_result: bool = True) -> dict[str, Any]:
    surface = run_vnext_surface_sync_audit(write_result=True)
    version = run_vnext_package_version_audit(write_result=True)
    residualops = run_residualops_alignment_audit(write_result=True)
    capability = run_capability_trust_claim_audit(write_result=True)
    router = run_objective_router_claim_audit(write_result=True)
    receipt = run_execution_receipt_claim_audit(write_result=True)
    probe = run_probe_claim_audit(write_result=True)
    secrets = run_no_secrets_audit()
    save_no_secrets_audit(secrets)
    launch = run_launch_claim_guard()
    smoke = run_smoke_all(write_result=True)

    claim_tokens = [capability["overall_token"], router["overall_token"], receipt["overall_token"], probe["overall_token"]]
    checks = {
        "surface_sync": surface["decision"],
        "version_audit": version["decision"],
        "residualops_alignment": residualops["decision"],
        "vnext_claim_audits": "PASS" if all(token == "PASS" for token in claim_tokens) else "BLOCK",
        "no_secrets": "PASS" if not secrets.get("findings") else "BLOCK",
        "launch_claim_guard": launch.get("overall_token", launch.get("token", "UNKNOWN")),
        "smoke_all": "PASS" if smoke.get("pass") is True or smoke.get("overall_token") == "PASS" else "HOLD",
    }
    warnings: list[str] = []
    errors: list[str] = []
    if checks["surface_sync"].startswith("BLOCK"):
        errors.append("Surface sync has missing required REST/MCP surfaces or overclaims.")
    if checks["residualops_alignment"].startswith("BLOCK"):
        errors.append("ResidualOps alignment has action or security overclaim.")
    if checks["vnext_claim_audits"] != "PASS":
        errors.append("One or more vNext claim audits failed.")
    if checks["no_secrets"] != "PASS":
        errors.append("No-secrets audit has real findings.")
    if checks["launch_claim_guard"] != "PASS":
        errors.append("Launch claim guard did not pass.")
    if checks["surface_sync"] == "HOLD_DOCS_INCOMPLETE":
        warnings.append("Surface docs are incomplete.")
    if checks["version_audit"] == "HOLD_VERSION_DECISION":
        warnings.append("Choose package/server version 0.3.0 or 0.3.0a1 before PyPI upload.")
    if checks["residualops_alignment"] == "HOLD_ALIGNMENT_DOCS_NEEDED":
        warnings.append("ResidualOps alignment docs need more vocabulary coverage.")
    if errors:
        decision = "BLOCK_OVERCLAIM" if any("claim" in error.lower() or "overclaim" in error.lower() for error in errors) else "BLOCK_SURFACE_MISSING"
    elif checks["version_audit"] == "HOLD_VERSION_DECISION":
        decision = "HOLD_VERSION_DECISION"
    elif warnings:
        decision = "HOLD_DOCS_INCOMPLETE"
    else:
        decision = "PASS_READY_TO_RESUME_8Q_A"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "overall_token": "PASS" if decision.startswith("PASS") else ("BLOCK" if decision.startswith("BLOCK") else "HOLD"),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "pytest_result": "not_checked_by_gate",
        "safe_to_resume_8q_a": decision in {"PASS_READY_TO_RESUME_8Q_A", "HOLD_VERSION_DECISION"},
        "claim_boundary": "Distribution readiness is not product, security, legal, safety, or quality readiness.",
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "external_tool_execution": False,
        "live_mcp_call_performed": False,
        "token_printed": False,
        "next_action": "Resolve version decision, then resume 8Q-A local build/twine check. Do not upload yet.",
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
        _write_summary(result)
    return result


def main() -> None:
    result = run_vnext_distribution_gate()
    print(
        "vnext_distribution_gate: "
        f"{result['decision']} safe_to_resume_8q_a={result['safe_to_resume_8q_a']}"
    )


if __name__ == "__main__":
    main()
