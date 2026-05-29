from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .datacapsule_pilot_packager import (
    EVAL_LEAKAGE_PATH,
    FEEDBACK_MEMORY_PATH,
    KNOWN_LIMITS_PATH,
    MANIFEST_PATH,
    PRIVACY_RISK_PATH,
    RECEIPT_PATH,
    REDACTION_REPORT_PATH,
    REVIEWER_READOUT_PATH,
    SOURCE_RIGHTS_PATH,
    USE_BOUNDARY_PATH,
    package_datacapsule_pilot,
)


OUTPUT_DIR = Path("public_launch") / "roe10"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE10_DATACAPSULE_PILOT_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE10_DATACAPSULE_PILOT_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE10_NEXT_ACTIONS.md"

RISKY_PATTERNS = [
    ("overclaim", re.compile(r"\blegal\s+compliance\b", re.I)),
    ("overclaim", re.compile(r"\bprivacy\s+compliant\b", re.I)),
    ("overclaim", re.compile(r"\blicense\s+cleared\b", re.I)),
    ("overclaim", re.compile(r"\beval\s+clean\b", re.I)),
    ("overclaim", re.compile(r"\bdataset\s+safe\b", re.I)),
    ("overclaim", re.compile(r"\bdata\s+quality\s+guaranteed\b", re.I)),
    ("overclaim", re.compile(r"\btraining\s+authorized\b", re.I)),
    ("overclaim", re.compile(r"\baction\s+authorized\b", re.I)),
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
    return f"""# ROE-10 DataCapsule Pilot Summary

Gate decision: `{gate['decision']}`

Pilot: `{receipt.get('pilot_id', 'unknown')}`

| Field | Value |
| --- | --- |
| ALLOW | `{summary.get('allow_count', 0)}` |
| HOLD | `{summary.get('hold_count', 0)}` |
| BLOCK | `{summary.get('block_count', 0)}` |
| Capsule decision | `{receipt.get('capsule_decision', 'unknown')}` |
| Redaction | `{gate['redaction_decision']}` |
| Raw content inspected | `False` |
| External network used | `False` |
| Data uploaded/trained | `False` |

This is a local/offline manifest review artifact. It is not legal advice, not a privacy audit, not license clearance, not evaluation-cleanliness proof, not data quality guarantee, and not training or action authorization.
"""


def build_next_actions_markdown(gate: dict[str, Any]) -> str:
    if gate["decision"] == "PASS_FIRST_DATACAPSULE_PILOT_RECEIPT_READY":
        next_action = "Use the sample as a reviewer bundle shape, then collect an owner-consented manifest with rights, privacy, and split-policy evidence."
    else:
        next_action = "Resolve ROE-10 HOLD/BLOCK items before sharing the DataCapsule pilot bundle."
    return f"""# ROE-10 Next Actions

Decision: `{gate['decision']}`

Recommended next action: {next_action}

Do not crawl, fetch URLs, inspect raw private content, upload data, train models, request tokens, or treat this receipt as legal/privacy/license/evaluation proof.
"""


def run_roe10_gate(write_result: bool = True, ensure_sample: bool = True) -> dict[str, Any]:
    if ensure_sample and not (_repo_root() / RECEIPT_PATH).exists():
        package_datacapsule_pilot(sample=True)

    receipt = _read_json(RECEIPT_PATH)
    redaction = _read_json(REDACTION_REPORT_PATH)
    memory = _read_json(FEEDBACK_MEMORY_PATH)
    artifacts = [
        _artifact_record(MANIFEST_PATH, "corpus_manifest"),
        _artifact_record(SOURCE_RIGHTS_PATH, "source_rights_summary"),
        _artifact_record(PRIVACY_RISK_PATH, "privacy_risk_summary"),
        _artifact_record(EVAL_LEAKAGE_PATH, "eval_leakage_summary"),
        _artifact_record(USE_BOUNDARY_PATH, "use_boundary"),
        _artifact_record(RECEIPT_PATH, "pilot_receipt"),
        _artifact_record(REVIEWER_READOUT_PATH, "reviewer_readout"),
        _artifact_record(REDACTION_REPORT_PATH, "redaction_report"),
        _artifact_record(FEEDBACK_MEMORY_PATH, "feedback_memory_entry"),
        _artifact_record(KNOWN_LIMITS_PATH, "known_limits"),
    ]
    missing = [item["path"] for item in artifacts if not item["exists"]]
    claim_findings = _scan_claims(
        [
            MANIFEST_PATH,
            SOURCE_RIGHTS_PATH,
            PRIVACY_RISK_PATH,
            EVAL_LEAKAGE_PATH,
            USE_BOUNDARY_PATH,
            RECEIPT_PATH,
            REVIEWER_READOUT_PATH,
            FEEDBACK_MEMORY_PATH,
            KNOWN_LIMITS_PATH,
        ]
    )
    flags = {
        "raw_content_inspected": bool(receipt.get("raw_content_inspected", False)),
        "external_network_used": bool(receipt.get("external_network_used", False)),
        "crawler_used": bool(receipt.get("crawler_used", False)),
        "data_uploaded": bool(receipt.get("data_uploaded", False)),
        "model_trained": bool(receipt.get("model_trained", False)),
        "external_api_used": bool(receipt.get("external_api_used", False)),
        "github_api_used": bool(receipt.get("github_api_used", False)),
    }
    if flags["raw_content_inspected"]:
        decision = "BLOCK_RAW_CONTENT_INSPECTION"
    elif flags["external_network_used"] or flags["crawler_used"] or flags["external_api_used"] or flags["github_api_used"]:
        decision = "BLOCK_EXTERNAL_NETWORK"
    elif flags["data_uploaded"] or flags["model_trained"]:
        decision = "BLOCK_DATA_UPLOAD_OR_TRAINING"
    elif missing:
        missing_set = set(missing)
        if str(SOURCE_RIGHTS_PATH).replace("\\", "/") in missing_set:
            decision = "HOLD_MISSING_RIGHTS_SUMMARY"
        elif str(PRIVACY_RISK_PATH).replace("\\", "/") in missing_set:
            decision = "HOLD_MISSING_PRIVACY_SUMMARY"
        elif str(EVAL_LEAKAGE_PATH).replace("\\", "/") in missing_set:
            decision = "HOLD_MISSING_EVAL_LEAKAGE_SUMMARY"
        else:
            decision = "HOLD_MISSING_READOUT"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT":
        decision = "BLOCK_SECRET_FINDING"
    elif redaction.get("decision") == "HOLD_REVIEW_RECOMMENDED":
        decision = "HOLD_REDACTION_REVIEW"
    elif claim_findings:
        finding_types = {finding["finding_type"] for finding in claim_findings}
        decision = "BLOCK_PRIVATE_KERNEL_EXPOSED" if "private_kernel" in finding_types else "BLOCK_OVERCLAIM"
    else:
        decision = "PASS_FIRST_DATACAPSULE_PILOT_RECEIPT_READY"

    result = {
        "schema": "ResidualOps_ROE10DataCapsulePilotGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "pilot_id": receipt.get("pilot_id", ""),
        "capsule_decision": receipt.get("capsule_decision", ""),
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "feedback_status": memory.get("feedback_status", "unknown"),
        "artifact_count": len(artifacts),
        "missing_artifacts": missing,
        "artifacts": artifacts,
        "claim_finding_count": len(claim_findings),
        "claim_findings": claim_findings[:100],
        **flags,
        "data_trained": flags["model_trained"],
        "review_comment_posted": False,
        "community_post_performed": False,
        "token_printed": False,
        "private_kernel_exposed": decision == "BLOCK_PRIVATE_KERNEL_EXPOSED",
        "can_certify_rights": False,
        "can_certify_privacy": False,
        "can_certify_quality": False,
        "can_prove_eval_cleanliness": False,
        "can_authorize_training": False,
        "can_authorize_action": False,
    }
    if write_result:
        _write_json(GATE_RESULT_PATH, result)
        _write_text(SUMMARY_PATH, build_summary_markdown(receipt, result))
        _write_text(NEXT_ACTIONS_PATH, build_next_actions_markdown(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-10 DataCapsule pilot receipt gate.")
    parser.add_argument("--no-sample", action="store_true", help="Do not generate the sample receipt before gating.")
    parser.add_argument("--no-write", action="store_true", help="Run gate without writing public outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe10_gate(write_result=not args.no_write, ensure_sample=not args.no_sample)
    print(f"roe10_datacapsule_pilot_gate: {result['decision']} redaction={result['redaction_decision']}")


if __name__ == "__main__":
    main()
