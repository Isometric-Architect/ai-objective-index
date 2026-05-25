from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import TOKEN_PATTERNS, _repo_root
from .residualops_onboarding_kit import ONBOARDING_KIT_PATH, run_roe5_claim_audit
from .residualops_public_private_alignment_audit import run_public_private_alignment_audit


OUTPUT_DIR = Path("public_launch") / "roe6"
PACKAGE_RESULT_PATH = OUTPUT_DIR / "ROE6_PILOT_FEEDBACK_MEMORY_RESULT.json"
RECEIPT_TEMPLATE_PATH = OUTPUT_DIR / "ROE6_PILOT_RECEIPT_TEMPLATE.json"
INTAKE_GATE_PATH = OUTPUT_DIR / "ROE6_RECEIPT_INTAKE_GATE.json"
FEEDBACK_MEMORY_PATH = OUTPUT_DIR / "ROE6_PILOT_FEEDBACK_MEMORY.json"
OUTCOME_SUMMARY_PATH = OUTPUT_DIR / "ROE6_PILOT_OUTCOME_SUMMARY.md"
CLAIM_AUDIT_PATH = OUTPUT_DIR / "ROE6_CLAIM_BOUNDARY_AUDIT.json"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "ROE6_ARTIFACT_MANIFEST.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "ROE6_NEXT_STEPS.md"

VERTICALS = {
    "agentsec": "AgentSec-8",
    "qira": "QIRA-9",
    "datacapsule": "DataCapsule-7",
}

OUTCOMES = {"allow", "hold", "block", "partial", "fail"}

MUST_NOT_CLAIM = [
    "verified",
    "safe",
    "security certified",
    "quality guaranteed",
    "production ready",
    "legal/privacy/license/evaluation proof",
    "purchasing advice",
    "action authorization",
]

RISKY_PATTERNS = [
    ("overclaim", re.compile(r"\bverified\s+capability\b", re.I)),
    ("overclaim", re.compile(r"\bsafe\s+tool\b", re.I)),
    ("overclaim", re.compile(r"\bsecurity\s+certified\b", re.I)),
    ("overclaim", re.compile(r"\bquality\s+guaranteed\b", re.I)),
    ("overclaim", re.compile(r"\bproduction\s+ready\b", re.I)),
    ("overclaim", re.compile(r"\baction\s+authorized\b", re.I)),
    ("overclaim", re.compile(r"\blegal\s+sufficiency\s+confirmed\b", re.I)),
    ("private_kernel", re.compile(r"\bprovider\s+trust\s+prior\s*[:=]\s*\d", re.I)),
    ("private_kernel", re.compile(r"\bprivate\s+ranking\s+weights?\s*[:=]\s*\d", re.I)),
    ("private_kernel", re.compile(r"\bprivate\s+negative-control\s+seed\s*[:=]", re.I)),
    ("private_kernel", re.compile(r"\bcommercial\s+routing\s+policy\s*[:=]\s*\d", re.I)),
]

SAFE_CONTEXT = [
    "not ",
    "no ",
    "do not",
    "does not",
    "cannot ",
    "without ",
    "must not",
    "must_not_claim",
    "claim boundary",
    "remain private",
    "remains private",
    "non-public",
]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any], root: Path | None = None) -> Path:
    base = root or _repo_root()
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _write_text(path: Path, text: str, root: Path | None = None) -> Path:
    base = root or _repo_root()
    destination = base / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _read_json(path: Path, root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    full = base / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _file_record(relative: Path, role: str, root: Path | None = None) -> dict[str, Any]:
    base = root or _repo_root()
    path = base / relative
    exists = path.exists() and path.is_file()
    return {
        "path": str(relative).replace("\\", "/"),
        "role": role,
        "exists": exists,
        "size_bytes": path.stat().st_size if exists else 0,
        "sha256": _sha256(path) if exists else "",
    }


def _as_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _contains_token_like(value: Any) -> bool:
    text = _as_text(value)
    return any(pattern.search(text) for pattern in TOKEN_PATTERNS)


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, str):
        text = value
        for pattern in TOKEN_PATTERNS:
            text = pattern.sub("[redacted]", text)
        return text
    return value


def _claim_scan_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _claim_scan_payload(item)
            for key, item in value.items()
            if str(key) not in {"must_not_claim", "claim_ceiling"}
        }
    if isinstance(value, list):
        return [_claim_scan_payload(item) for item in value]
    return value


def _safe_line(line: str, previous_lines: list[str] | None = None) -> bool:
    lowered = line.lower()
    if any(marker in lowered for marker in SAFE_CONTEXT):
        return True
    context = "\n".join(previous_lines or []).lower()
    return any(marker in context for marker in ["forbidden claims", "must not claim", "must_not_claim", "known limits"])


def _candidate_files(root: Path, paths: list[Path] | None = None) -> list[Path]:
    selected = paths or [
        Path("README.md"),
        Path("CHANGELOG.md"),
        Path("docs") / "roe6_pilot_feedback_memory.md",
        Path("docs") / "residualops_pilot_receipt_intake.md",
        Path("docs") / "residualops_feedback_memory_limitations.md",
        OUTPUT_DIR,
    ]
    files: list[Path] = []
    for relative in selected:
        path = root / relative
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt", ".yml", ".yaml"}:
            files.append(path)
        elif path.is_dir():
            files.extend(
                child
                for child in path.rglob("*")
                if child.is_file() and child.suffix.lower() in {".md", ".json", ".txt", ".yml", ".yaml"}
            )
    return sorted(set(files))


def build_pilot_receipt_template() -> dict[str, Any]:
    return {
        "schema": "ResidualOps_PilotReceipt/v0.1",
        "receipt_id": "roe6-template-receipt",
        "vertical_id": "agentsec",
        "package": "AgentSec-8",
        "repository_alias": "owner-approved-repository-alias",
        "workflow_artifact_name": "agentsec-local-review-artifact",
        "owner_consent_confirmed": False,
        "receipt_origin": "manual_operator_entry",
        "outcome": "hold",
        "hold_reasons": ["owner consent must be recorded before workflow enablement"],
        "block_reasons": [],
        "missing_inputs": ["owner consent record", "repository-supplied manifest artifact"],
        "feedback_notes": "Replace this placeholder with non-secret, non-private pilot notes.",
        "recommended_follow_up": "prepare manual workflow_dispatch run after consent",
        "claim_ceiling": "local pilot feedback only; not verification, certification, product readiness, legal/privacy/license/evaluation proof, purchasing advice, or action authorization",
        "must_not_claim": MUST_NOT_CLAIM,
        "external_actions_performed": False,
        "workflow_enabled_by_aoi": False,
        "github_api_used_by_aoi": False,
        "token_printed": False,
        "private_kernel_exposed": False,
        "generated_at": _timestamp(),
    }


def validate_pilot_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    sanitized = _sanitize(receipt)

    if _contains_token_like(receipt):
        errors.append("token-like string detected in receipt")

    vertical_id = str(receipt.get("vertical_id", "")).strip().lower()
    outcome = str(receipt.get("outcome", "")).strip().lower()
    if not vertical_id:
        errors.append("missing vertical_id")
    elif vertical_id not in VERTICALS:
        errors.append("unsupported vertical_id")
    if not outcome:
        errors.append("missing outcome")
    elif outcome not in OUTCOMES:
        errors.append("unsupported outcome")
    if not str(receipt.get("repository_alias", "")).strip():
        errors.append("missing repository_alias")

    text = _as_text(_claim_scan_payload(receipt))
    for finding_type, pattern in RISKY_PATTERNS:
        if pattern.search(text):
            errors.append(f"{finding_type} phrase detected: {pattern.pattern}")
            break

    owner_consent = bool(receipt.get("owner_consent_confirmed", False))
    if not owner_consent:
        warnings.append("owner consent is not confirmed; receipt can only be used as a preparation note")

    if any(error.startswith("token-like") for error in errors):
        decision = "BLOCK_TOKEN_OR_SECRET_FINDING"
    elif any("overclaim" in error for error in errors):
        decision = "BLOCK_OVERCLAIM"
    elif any("private_kernel" in error for error in errors):
        decision = "BLOCK_PRIVATE_KERNEL_EXPOSURE"
    elif errors:
        decision = "INVALID_PILOT_RECEIPT"
    elif not owner_consent:
        decision = "HOLD_OWNER_CONSENT_MISSING"
    else:
        decision = "RECEIPT_ACCEPTED"

    return {
        "schema": "ResidualOps_PilotReceiptValidation/v0.1",
        "generated_at": _timestamp(),
        "receipt_id": str(receipt.get("receipt_id", "")),
        "decision": decision,
        "valid": decision in {"RECEIPT_ACCEPTED", "HOLD_OWNER_CONSENT_MISSING"},
        "errors": errors,
        "warnings": warnings,
        "sanitized_receipt": sanitized,
        "can_influence_memory": decision == "RECEIPT_ACCEPTED",
        "can_enable_workflow": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_prove_readiness": False,
        "can_authorize_action": False,
        "token_printed": False,
    }


def build_feedback_memory(receipts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    active_receipts = receipts or []
    accepted = [receipt for receipt in active_receipts if validate_pilot_receipt(receipt)["decision"] == "RECEIPT_ACCEPTED"]
    outcome_counts = Counter(str(receipt.get("outcome", "")).lower() for receipt in accepted)
    vertical_counts = Counter(str(receipt.get("vertical_id", "")).lower() for receipt in accepted)
    hold_reasons: Counter[str] = Counter()
    block_reasons: Counter[str] = Counter()
    missing_inputs: Counter[str] = Counter()
    for receipt in accepted:
        hold_reasons.update(str(item) for item in receipt.get("hold_reasons", []) if str(item).strip())
        block_reasons.update(str(item) for item in receipt.get("block_reasons", []) if str(item).strip())
        missing_inputs.update(str(item) for item in receipt.get("missing_inputs", []) if str(item).strip())

    if not accepted:
        decision = "HOLD_NO_PILOT_RECEIPTS_YET"
        next_action = "collect one owner-consented manual pilot receipt before changing routing or workflow guidance"
    elif outcome_counts.get("block", 0) or outcome_counts.get("fail", 0):
        decision = "HOLD_REVIEW_FAILURE_SIGNALS"
        next_action = "review failure signals before any second pilot run"
    else:
        decision = "PASS_PILOT_FEEDBACK_MEMORY_AVAILABLE"
        next_action = "summarize accepted receipt signals without treating them as verification"

    return {
        "schema": "ResidualOps_PilotFeedbackMemory/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "receipt_count": len(accepted),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "vertical_counts": dict(sorted(vertical_counts.items())),
        "top_hold_reasons": hold_reasons.most_common(10),
        "top_block_reasons": block_reasons.most_common(10),
        "top_missing_inputs": missing_inputs.most_common(10),
        "recommended_next_action": next_action,
        "memory_status": "NO_RECEIPTS" if not accepted else "RECEIPTS_AVAILABLE",
        "can_upgrade_to_verified": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
    }


def run_roe6_claim_audit(
    write_result: bool = True,
    root: Path | None = None,
    paths: list[Path] | None = None,
) -> dict[str, Any]:
    base = root or _repo_root()
    findings: list[dict[str, Any]] = []
    for path in _candidate_files(base, paths):
        rel = str(path.relative_to(base)).replace("\\", "/")
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_number, line in enumerate(lines, start=1):
            if _safe_line(line, lines[max(0, line_number - 6) : line_number - 1]):
                continue
            for finding_type, pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        {
                            "path": rel,
                            "line": line_number,
                            "finding_type": finding_type,
                            "pattern": pattern.pattern,
                        }
                    )
                    break
    finding_types = {finding["finding_type"] for finding in findings}
    if "private_kernel" in finding_types:
        decision = "BLOCK_ROE6_PRIVATE_KERNEL_LEAK"
    elif "overclaim" in finding_types:
        decision = "BLOCK_ROE6_OVERCLAIM"
    else:
        decision = "PASS_ROE6_CLAIM_BOUNDARY"
    result = {
        "schema": "ResidualOps_ROE6ClaimBoundaryAudit/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "finding_count": len(findings),
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
        "private_kernel_exposed": "private_kernel" in finding_types,
    }
    if write_result:
        _write_json(CLAIM_AUDIT_PATH, result, root=base)
    return result


def outcome_summary_markdown(memory: dict[str, Any], intake_gate: dict[str, Any]) -> str:
    return f"""# ROE-6 Pilot Outcome Summary

Feedback memory decision: `{memory['decision']}`

Receipt intake gate: `{intake_gate['decision']}`

Accepted receipt count: `{memory['receipt_count']}`

## Interpretation

ROE-6 is ready to receive manual pilot receipts, but receipt memory is not verification, certification, product-readiness proof, legal/privacy/license/evaluation proof, purchasing advice, or action authorization.

## Next Operator Move

{memory['recommended_next_action']}
"""


def next_steps_markdown(result: dict[str, Any]) -> str:
    if result["decision"] == "PASS_ROE6_PILOT_FEEDBACK_MEMORY_READY":
        next_step = "Run exactly one owner-consented AgentSec pilot manually and submit a non-secret pilot receipt."
    else:
        next_step = "Resolve ROE-6 HOLD/BLOCK issues before collecting pilot receipts."
    return f"""# ROE-6 Next Steps

Decision: `{result['decision']}`

Recommended next step: {next_step}

Do not enable workflows, call GitHub APIs, post comments, request tokens, store partner secrets, or treat pilot feedback as verification.
"""


def build_artifact_manifest(root: Path | None = None) -> dict[str, Any]:
    paths = [
        PACKAGE_RESULT_PATH,
        RECEIPT_TEMPLATE_PATH,
        INTAKE_GATE_PATH,
        FEEDBACK_MEMORY_PATH,
        OUTCOME_SUMMARY_PATH,
        CLAIM_AUDIT_PATH,
        NEXT_STEPS_PATH,
    ]
    records = [_file_record(path, "roe6_output", root=root) for path in paths]
    missing = [record["path"] for record in records if not record["exists"]]
    return {
        "schema": "ResidualOps_ROE6ArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_ROE6_ARTIFACT_MANIFEST" if not missing else "HOLD_ROE6_ARTIFACT_MISSING",
        "artifacts": records,
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }


def build_package_result(
    intake_gate: dict[str, Any],
    feedback_memory: dict[str, Any],
    claim_audit: dict[str, Any],
    alignment: dict[str, Any],
    roe5_claim_audit: dict[str, Any],
    roe5_kit: dict[str, Any],
) -> dict[str, Any]:
    issues: list[str] = []
    decision = "PASS_ROE6_PILOT_FEEDBACK_MEMORY_READY"
    if roe5_kit.get("decision") != "PASS_ROE5_PORTFOLIO_ONBOARDING_KIT":
        decision = "HOLD_ROE5_ONBOARDING_REQUIRED"
        issues.append("ROE-5 onboarding kit is not PASS")
    elif roe5_claim_audit.get("decision") != "PASS_ROE5_CLAIM_BOUNDARY":
        decision = "HOLD_ROE5_CLAIM_BOUNDARY_REQUIRED"
        issues.append("ROE-5 claim audit is not PASS")
    elif claim_audit["decision"].startswith("BLOCK"):
        decision = claim_audit["decision"]
        issues.append("ROE-6 claim audit failed")
    elif alignment["decision"].startswith("BLOCK"):
        decision = "BLOCK_ROE6_PUBLIC_PRIVATE_ALIGNMENT"
        issues.append(f"public/private alignment {alignment['decision']}")

    return {
        "schema": "ResidualOps_ROE6PilotFeedbackMemoryResult/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "issues": issues,
        "roe5_kit_decision": roe5_kit.get("decision", "UNKNOWN"),
        "roe5_claim_audit_decision": roe5_claim_audit.get("decision", "UNKNOWN"),
        "receipt_intake_gate_decision": intake_gate["decision"],
        "feedback_memory_decision": feedback_memory["decision"],
        "claim_audit_decision": claim_audit["decision"],
        "public_private_alignment_decision": alignment["decision"],
        "external_actions_performed": False,
        "workflow_enabled": False,
        "github_api_used": False,
        "review_comment_posted": False,
        "crawler_used": False,
        "network_used": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "token_printed": False,
        "private_kernel_exposed": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_prove_readiness": False,
        "can_authorize_action": False,
    }


def run_pilot_feedback_memory(write_result: bool = True) -> dict[str, Any]:
    template = build_pilot_receipt_template()
    intake_gate = validate_pilot_receipt(template)
    memory = build_feedback_memory([])
    if write_result:
        _write_json(RECEIPT_TEMPLATE_PATH, template)
        _write_json(INTAKE_GATE_PATH, intake_gate)
        _write_json(FEEDBACK_MEMORY_PATH, memory)
        _write_text(OUTCOME_SUMMARY_PATH, outcome_summary_markdown(memory, intake_gate))
    claim_audit = run_roe6_claim_audit(write_result=write_result)
    alignment = run_public_private_alignment_audit(
        write_result=False,
        paths=[Path("docs"), OUTPUT_DIR, Path("README.md"), Path("CHANGELOG.md")],
    )
    roe5_claim_audit = run_roe5_claim_audit(write_result=False)
    roe5_kit = _read_json(ONBOARDING_KIT_PATH)
    result = build_package_result(intake_gate, memory, claim_audit, alignment, roe5_claim_audit, roe5_kit)
    if write_result:
        _write_json(PACKAGE_RESULT_PATH, result)
        _write_text(NEXT_STEPS_PATH, next_steps_markdown(result))
        _write_json(ARTIFACT_MANIFEST_PATH, build_artifact_manifest())
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build ROE-6 pilot receipt intake and feedback memory artifacts.")
    parser.add_argument("--audit-only", action="store_true", help="Run ROE-6 claim audit only.")
    parser.add_argument("--no-write", action="store_true", help="Build in memory without writing public outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_only:
        result = run_roe6_claim_audit(write_result=not args.no_write)
        print(f"residualops_pilot_feedback_claim_audit: {result['decision']} findings={result['finding_count']}")
        return
    result = run_pilot_feedback_memory(write_result=not args.no_write)
    print(f"residualops_pilot_feedback_memory: {result['decision']} memory={result['feedback_memory_decision']}")


if __name__ == "__main__":
    main()
