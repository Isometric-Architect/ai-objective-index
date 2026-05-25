from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root
from .residualops_pilot_feedback_memory import (
    FEEDBACK_MEMORY_PATH as ROE6_FEEDBACK_MEMORY_PATH,
    PACKAGE_RESULT_PATH as ROE6_PACKAGE_RESULT_PATH,
    build_feedback_memory,
    build_pilot_receipt_template,
    run_roe6_claim_audit,
)
from .residualops_public_private_alignment_audit import run_public_private_alignment_audit


OUTPUT_DIR = Path("public_launch") / "roe7"
PACKAGE_RESULT_PATH = OUTPUT_DIR / "ROE7_PILOT_READOUT_GATE_RESULT.json"
PILOT_READOUT_PATH = OUTPUT_DIR / "ROE7_PILOT_RECEIPT_READOUT.json"
SECOND_RUN_GATE_PATH = OUTPUT_DIR / "ROE7_SECOND_RUN_DECISION_GATE.json"
OPERATOR_PACKET_PATH = OUTPUT_DIR / "ROE7_OPERATOR_REVIEW_PACKET.md"
CLAIM_AUDIT_PATH = OUTPUT_DIR / "ROE7_CLAIM_BOUNDARY_AUDIT.json"
ARTIFACT_MANIFEST_PATH = OUTPUT_DIR / "ROE7_ARTIFACT_MANIFEST.json"
NEXT_STEPS_PATH = OUTPUT_DIR / "ROE7_NEXT_STEPS.md"

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
        Path("docs") / "roe7_pilot_readout_second_run_gate.md",
        Path("docs") / "residualops_second_run_decision_gate.md",
        Path("docs") / "residualops_pilot_readout_limitations.md",
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


def build_pilot_receipt_readout(
    feedback_memory: dict[str, Any] | None = None,
    roe6_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    memory = feedback_memory or _read_json(ROE6_FEEDBACK_MEMORY_PATH)
    package_result = roe6_result or _read_json(ROE6_PACKAGE_RESULT_PATH)
    receipt_count = int(memory.get("receipt_count") or 0)
    outcome_counts = memory.get("outcome_counts") if isinstance(memory.get("outcome_counts"), dict) else {}
    hold_reasons = memory.get("top_hold_reasons") if isinstance(memory.get("top_hold_reasons"), list) else []
    block_reasons = memory.get("top_block_reasons") if isinstance(memory.get("top_block_reasons"), list) else []

    if package_result.get("decision") != "PASS_ROE6_PILOT_FEEDBACK_MEMORY_READY":
        decision = "HOLD_ROE6_FEEDBACK_MEMORY_REQUIRED"
        next_action = "regenerate ROE-6 before evaluating pilot receipt readout"
    elif receipt_count == 0:
        decision = "HOLD_FIRST_PILOT_RECEIPT_REQUIRED"
        next_action = "run one owner-consented manual pilot and record a non-secret receipt"
    elif int(outcome_counts.get("block", 0)) or int(outcome_counts.get("fail", 0)):
        decision = "HOLD_FAILURE_REVIEW_REQUIRED"
        next_action = "review block/fail signals before preparing a second run"
    elif int(outcome_counts.get("hold", 0)) or int(outcome_counts.get("partial", 0)):
        decision = "HOLD_SECOND_RUN_REVIEW_REQUIRED"
        next_action = "operator review is required before any second run"
    else:
        decision = "PASS_READOUT_READY_FOR_SECOND_RUN_GATE"
        next_action = "run second-run gate with explicit owner consent and operator review"

    return {
        "schema": "ResidualOps_ROE7PilotReceiptReadout/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "receipt_count": receipt_count,
        "outcome_counts": outcome_counts,
        "top_hold_reasons": hold_reasons[:10],
        "top_block_reasons": block_reasons[:10],
        "recommended_next_action": next_action,
        "can_prepare_second_run_gate": decision in {"PASS_READOUT_READY_FOR_SECOND_RUN_GATE", "HOLD_SECOND_RUN_REVIEW_REQUIRED"},
        "can_upgrade_to_verified": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "github_api_used": False,
        "token_printed": False,
    }


def build_second_run_decision_gate(
    readout: dict[str, Any],
    owner_consent_confirmed: bool = False,
    operator_review_complete: bool = False,
) -> dict[str, Any]:
    readout_decision = str(readout.get("decision", ""))
    if readout_decision == "HOLD_ROE6_FEEDBACK_MEMORY_REQUIRED":
        decision = "HOLD_ROE6_FEEDBACK_MEMORY_REQUIRED"
        reason = "ROE-6 feedback memory is not ready"
    elif readout_decision == "HOLD_FIRST_PILOT_RECEIPT_REQUIRED":
        decision = "HOLD_FIRST_PILOT_RECEIPT_REQUIRED"
        reason = "no accepted pilot receipt exists yet"
    elif readout_decision == "HOLD_FAILURE_REVIEW_REQUIRED":
        decision = "HOLD_FAILURE_REVIEW_REQUIRED"
        reason = "fail or block signal requires review before a second run"
    elif not owner_consent_confirmed:
        decision = "HOLD_OWNER_CONSENT_REQUIRED_FOR_SECOND_RUN"
        reason = "repository owner consent must be recorded before a second manual run"
    elif not operator_review_complete:
        decision = "HOLD_OPERATOR_REVIEW_REQUIRED"
        reason = "operator review must confirm receipt notes before a second manual run"
    else:
        decision = "PASS_SECOND_RUN_MANUAL_DRY_RUN_READY"
        reason = "second manual run can be prepared by the owner, but AOI does not enable it"

    return {
        "schema": "ResidualOps_ROE7SecondRunDecisionGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "reason": reason,
        "readout_decision": readout_decision,
        "owner_consent_confirmed": owner_consent_confirmed,
        "operator_review_complete": operator_review_complete,
        "manual_second_run_only": True,
        "can_prepare_manual_second_run": decision == "PASS_SECOND_RUN_MANUAL_DRY_RUN_READY",
        "workflow_enabled_by_aoi": False,
        "github_api_used_by_aoi": False,
        "review_comment_posted": False,
        "external_actions_performed": False,
        "token_printed": False,
        "can_upgrade_to_verified": False,
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_authorize_action": False,
    }


def operator_review_packet_markdown(readout: dict[str, Any], gate: dict[str, Any]) -> str:
    return f"""# ROE-7 Operator Review Packet

Pilot readout decision: `{readout['decision']}`

Second-run gate decision: `{gate['decision']}`

Reason: {gate['reason']}

## Operator Checklist

- Confirm the repository owner consent record outside this public repo.
- Review the first pilot artifact and receipt notes.
- Keep any second run manual and owner initiated.
- Do not paste tokens, private repository data, partner strategy, or private kernel details into public artifacts.

## Boundary

This packet is a local readout and second-run gate. It is not verification, security certification, quality guarantee, product-readiness proof, legal/privacy/license/evaluation proof, purchasing advice, or action authorization.
"""


def run_roe7_claim_audit(
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
        decision = "BLOCK_ROE7_PRIVATE_KERNEL_LEAK"
    elif "overclaim" in finding_types:
        decision = "BLOCK_ROE7_OVERCLAIM"
    else:
        decision = "PASS_ROE7_CLAIM_BOUNDARY"
    result = {
        "schema": "ResidualOps_ROE7ClaimBoundaryAudit/v0.1",
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


def build_artifact_manifest(root: Path | None = None) -> dict[str, Any]:
    paths = [
        PACKAGE_RESULT_PATH,
        PILOT_READOUT_PATH,
        SECOND_RUN_GATE_PATH,
        OPERATOR_PACKET_PATH,
        CLAIM_AUDIT_PATH,
        NEXT_STEPS_PATH,
    ]
    records = [_file_record(path, "roe7_output", root=root) for path in paths]
    missing = [record["path"] for record in records if not record["exists"]]
    return {
        "schema": "ResidualOps_ROE7ArtifactManifest/v0.1",
        "generated_at": _timestamp(),
        "decision": "PASS_ROE7_ARTIFACT_MANIFEST" if not missing else "HOLD_ROE7_ARTIFACT_MISSING",
        "artifacts": records,
        "missing_artifacts": missing,
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
    }


def build_package_result(
    readout: dict[str, Any],
    gate: dict[str, Any],
    claim_audit: dict[str, Any],
    alignment: dict[str, Any],
    roe6_claim_audit: dict[str, Any],
    roe6_result: dict[str, Any],
) -> dict[str, Any]:
    issues: list[str] = []
    decision = "PASS_ROE7_PILOT_READOUT_GATE_READY"
    if roe6_result.get("decision") != "PASS_ROE6_PILOT_FEEDBACK_MEMORY_READY":
        decision = "HOLD_ROE6_FEEDBACK_MEMORY_REQUIRED"
        issues.append("ROE-6 feedback memory package is not PASS")
    elif roe6_claim_audit.get("decision") != "PASS_ROE6_CLAIM_BOUNDARY":
        decision = "HOLD_ROE6_CLAIM_BOUNDARY_REQUIRED"
        issues.append("ROE-6 claim audit is not PASS")
    elif claim_audit["decision"].startswith("BLOCK"):
        decision = claim_audit["decision"]
        issues.append("ROE-7 claim audit failed")
    elif alignment["decision"].startswith("BLOCK"):
        decision = "BLOCK_ROE7_PUBLIC_PRIVATE_ALIGNMENT"
        issues.append(f"public/private alignment {alignment['decision']}")

    return {
        "schema": "ResidualOps_ROE7PilotReadoutGateResult/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "issues": issues,
        "roe6_result_decision": roe6_result.get("decision", "UNKNOWN"),
        "roe6_claim_audit_decision": roe6_claim_audit.get("decision", "UNKNOWN"),
        "pilot_readout_decision": readout["decision"],
        "second_run_gate_decision": gate["decision"],
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


def next_steps_markdown(result: dict[str, Any]) -> str:
    if result["second_run_gate_decision"] == "HOLD_FIRST_PILOT_RECEIPT_REQUIRED":
        next_step = "Run one owner-consented AgentSec pilot manually and record a non-secret ROE-6 pilot receipt."
    elif result["second_run_gate_decision"].startswith("HOLD"):
        next_step = "Resolve the second-run gate HOLD before any further pilot run."
    else:
        next_step = "Prepare a second manual dry run under explicit owner consent and operator review."
    return f"""# ROE-7 Next Steps

Decision: `{result['decision']}`

Second-run gate: `{result['second_run_gate_decision']}`

Recommended next step: {next_step}

Do not enable workflows automatically, call GitHub APIs, post comments, request tokens, store partner secrets, or treat pilot readout as verification.
"""


def run_pilot_readout_gate(write_result: bool = True) -> dict[str, Any]:
    memory = _read_json(ROE6_FEEDBACK_MEMORY_PATH)
    if not memory:
        memory = build_feedback_memory([])
    roe6_result = _read_json(ROE6_PACKAGE_RESULT_PATH)
    readout = build_pilot_receipt_readout(memory, roe6_result)
    gate = build_second_run_decision_gate(readout)
    if write_result:
        _write_json(PILOT_READOUT_PATH, readout)
        _write_json(SECOND_RUN_GATE_PATH, gate)
        _write_text(OPERATOR_PACKET_PATH, operator_review_packet_markdown(readout, gate))
    claim_audit = run_roe7_claim_audit(write_result=write_result)
    alignment = run_public_private_alignment_audit(
        write_result=False,
        paths=[Path("docs"), OUTPUT_DIR, Path("README.md"), Path("CHANGELOG.md")],
    )
    roe6_claim_audit = run_roe6_claim_audit(write_result=False)
    result = build_package_result(readout, gate, claim_audit, alignment, roe6_claim_audit, roe6_result)
    if write_result:
        _write_json(PACKAGE_RESULT_PATH, result)
        _write_text(NEXT_STEPS_PATH, next_steps_markdown(result))
        _write_json(ARTIFACT_MANIFEST_PATH, build_artifact_manifest())
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build ROE-7 pilot receipt readout and second-run gate artifacts.")
    parser.add_argument("--audit-only", action="store_true", help="Run ROE-7 claim audit only.")
    parser.add_argument("--no-write", action="store_true", help="Build in memory without writing public outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.audit_only:
        result = run_roe7_claim_audit(write_result=not args.no_write)
        print(f"residualops_pilot_readout_claim_audit: {result['decision']} findings={result['finding_count']}")
        return
    result = run_pilot_readout_gate(write_result=not args.no_write)
    print(
        "residualops_pilot_readout_gate: "
        f"{result['decision']} second_run={result['second_run_gate_decision']}"
    )


if __name__ == "__main__":
    main()
