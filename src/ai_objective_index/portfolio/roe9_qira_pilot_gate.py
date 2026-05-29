from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .qira_pilot_packager import (
    BEHAVIOR_CONTRACT_PATH,
    CI_EVIDENCE_PATH,
    FEEDBACK_MEMORY_PATH,
    KNOWN_LIMITS_PATH,
    PATCH_CLASSIFICATION_PATH,
    RECEIPT_PATH,
    REDACTION_REPORT_PATH,
    REVIEWER_READOUT_PATH,
    TASK_PACKET_PATH,
    package_qira_pilot,
)


OUTPUT_DIR = Path("public_launch") / "roe9"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE9_QIRA_PILOT_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE9_QIRA_PILOT_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE9_NEXT_ACTIONS.md"

RISKY_PATTERNS = [
    ("overclaim", re.compile(r"\bcorrectness\s+proven\b", re.I)),
    ("overclaim", re.compile(r"\bverified\s+code\b", re.I)),
    ("overclaim", re.compile(r"\bcode\s+is\s+safe\b", re.I)),
    ("overclaim", re.compile(r"\bsecure\s+code\b", re.I)),
    ("overclaim", re.compile(r"\bsecurity\s+certified\b", re.I)),
    ("overclaim", re.compile(r"\bquality\s+guaranteed\b", re.I)),
    ("overclaim", re.compile(r"\bproduction\s+ready\b", re.I)),
    ("merge_deploy", re.compile(r"\bmerge\s+authorized\b", re.I)),
    ("merge_deploy", re.compile(r"\bdeploy\s+authorized\b", re.I)),
    ("external_action", re.compile(r"\bexternal\s+repo\s+mutation\s+allowed\b", re.I)),
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
    "known limits",
    "claim boundary",
]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _write_text(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scan_claims(paths: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for relative in paths:
        full = _repo_root() / relative
        if not full.exists() or not full.is_file():
            continue
        lines = full.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            if any(marker in lowered for marker in SAFE_CONTEXT):
                continue
            for finding_type, pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        {
                            "path": str(relative).replace("\\", "/"),
                            "line": line_number,
                            "finding_type": finding_type,
                            "pattern": pattern.pattern,
                        }
                    )
                    break
    return findings


def _artifact_record(path: Path, role: str) -> dict[str, Any]:
    full = _repo_root() / path
    exists = full.exists() and full.is_file()
    return {
        "path": str(path).replace("\\", "/"),
        "role": role,
        "exists": exists,
        "size_bytes": full.stat().st_size if exists else 0,
        "sha256": _sha256(full) if exists else "",
    }


def build_summary_markdown(receipt: dict[str, Any], gate: dict[str, Any]) -> str:
    summary = receipt.get("decision_summary", {}) if isinstance(receipt.get("decision_summary"), dict) else {}
    return f"""# ROE-9 QIRA Pilot Summary

Gate decision: `{gate['decision']}`

Pilot: `{receipt.get('pilot_id', 'unknown')}`

| Field | Value |
| --- | --- |
| ALLOW | `{summary.get('allow_count', 0)}` |
| HOLD | `{summary.get('hold_count', 0)}` |
| BLOCK | `{summary.get('block_count', 0)}` |
| Release gate decision | `{receipt.get('release_gate_decision', 'unknown')}` |
| Redaction | `{gate['redaction_decision']}` |
| GitHub API used | `False` |
| External repo modified | `False` |
| Merge/deploy performed | `False` |

This is a local/offline release-gate review artifact. It is not code correctness proof, not security certification, not a quality guarantee, and not merge or deploy authorization.
"""


def build_next_actions_markdown(gate: dict[str, Any]) -> str:
    if gate["decision"] == "PASS_FIRST_QIRA_PILOT_RECEIPT_READY":
        next_action = "Use the sample as a reviewer bundle shape, then collect an owner-consented QIRA pilot receipt with copied/local CI evidence."
    else:
        next_action = "Resolve ROE-9 HOLD/BLOCK items before sharing the QIRA pilot bundle."
    return f"""# ROE-9 Next Actions

Decision: `{gate['decision']}`

Recommended next action: {next_action}

Do not call GitHub APIs, mutate external repositories, post comments, merge, deploy, publish packages, request tokens, or treat this receipt as proof or certification.
"""


def run_roe9_gate(write_result: bool = True, ensure_sample: bool = True) -> dict[str, Any]:
    if ensure_sample and not (_repo_root() / RECEIPT_PATH).exists():
        package_qira_pilot(sample=True)

    receipt = _read_json(RECEIPT_PATH)
    redaction = _read_json(REDACTION_REPORT_PATH)
    memory = _read_json(FEEDBACK_MEMORY_PATH)
    artifacts = [
        _artifact_record(TASK_PACKET_PATH, "task_packet"),
        _artifact_record(PATCH_CLASSIFICATION_PATH, "patch_classification"),
        _artifact_record(BEHAVIOR_CONTRACT_PATH, "behavior_contract"),
        _artifact_record(CI_EVIDENCE_PATH, "ci_evidence_summary"),
        _artifact_record(RECEIPT_PATH, "pilot_receipt"),
        _artifact_record(REVIEWER_READOUT_PATH, "reviewer_readout"),
        _artifact_record(REDACTION_REPORT_PATH, "redaction_report"),
        _artifact_record(FEEDBACK_MEMORY_PATH, "feedback_memory_entry"),
        _artifact_record(KNOWN_LIMITS_PATH, "known_limits"),
    ]
    missing = [item["path"] for item in artifacts if not item["exists"]]
    claim_findings = _scan_claims(
        [
            TASK_PACKET_PATH,
            PATCH_CLASSIFICATION_PATH,
            BEHAVIOR_CONTRACT_PATH,
            CI_EVIDENCE_PATH,
            RECEIPT_PATH,
            REVIEWER_READOUT_PATH,
            FEEDBACK_MEMORY_PATH,
            KNOWN_LIMITS_PATH,
        ]
    )
    external_flags = {
        "github_api_used": bool(receipt.get("github_api_used", False)),
        "external_repo_modified": bool(receipt.get("external_repo_modified", False)),
        "external_actions_performed": bool(receipt.get("external_actions_performed", False)),
        "merge_performed": bool(receipt.get("merge_performed", False)),
        "deploy_performed": bool(receipt.get("deploy_performed", False)),
        "publish_performed": bool(receipt.get("publish_performed", False)),
    }
    boundary = receipt.get("claim_boundary", {}) if isinstance(receipt.get("claim_boundary"), dict) else {}
    merge_or_deploy_authorized = not bool(boundary.get("no_merge_authorization", True)) or not bool(boundary.get("no_deploy_authorization", True))

    if any(external_flags.values()):
        decision = "BLOCK_EXTERNAL_ACTION"
    elif merge_or_deploy_authorized:
        decision = "BLOCK_MERGE_OR_DEPLOY_AUTHORIZATION"
    elif missing:
        decision = "HOLD_MISSING_READOUT"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT":
        decision = "BLOCK_SECRET_FINDING"
    elif redaction.get("decision") == "HOLD_REVIEW_RECOMMENDED":
        decision = "HOLD_REDACTION_REVIEW"
    elif claim_findings:
        finding_types = {finding["finding_type"] for finding in claim_findings}
        if "private_kernel" in finding_types:
            decision = "BLOCK_PRIVATE_KERNEL_EXPOSED"
        elif "merge_deploy" in finding_types:
            decision = "BLOCK_MERGE_OR_DEPLOY_AUTHORIZATION"
        else:
            decision = "BLOCK_OVERCLAIM"
    else:
        decision = "PASS_FIRST_QIRA_PILOT_RECEIPT_READY"

    result = {
        "schema": "ResidualOps_ROE9QIRAPilotGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "pilot_id": receipt.get("pilot_id", ""),
        "release_gate_decision": receipt.get("release_gate_decision", ""),
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "feedback_status": memory.get("feedback_status", "unknown"),
        "artifact_count": len(artifacts),
        "missing_artifacts": missing,
        "artifacts": artifacts,
        "claim_finding_count": len(claim_findings),
        "claim_findings": claim_findings[:100],
        **external_flags,
        "review_comment_posted": False,
        "crawler_used": False,
        "network_used": False,
        "token_printed": False,
        "private_kernel_exposed": decision == "BLOCK_PRIVATE_KERNEL_EXPOSED",
        "can_prove_correctness": False,
        "can_certify_security": False,
        "can_guarantee_quality": False,
        "can_authorize_merge": False,
        "can_authorize_deploy": False,
    }
    if write_result:
        _write_json(GATE_RESULT_PATH, result)
        _write_text(SUMMARY_PATH, build_summary_markdown(receipt, result))
        _write_text(NEXT_ACTIONS_PATH, build_next_actions_markdown(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-9 QIRA pilot receipt gate.")
    parser.add_argument("--no-sample", action="store_true", help="Do not generate the sample receipt before gating.")
    parser.add_argument("--no-write", action="store_true", help="Run gate without writing public outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe9_gate(write_result=not args.no_write, ensure_sample=not args.no_sample)
    print(f"roe9_qira_pilot_gate: {result['decision']} redaction={result['redaction_decision']}")


if __name__ == "__main__":
    main()
