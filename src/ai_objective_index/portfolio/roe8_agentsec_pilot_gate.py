from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .agentsec_pilot_packager import (
    FEEDBACK_MEMORY_PATH,
    KNOWN_LIMITS_PATH,
    RECEIPT_PATH,
    REDACTION_REPORT_PATH,
    REVIEWER_READOUT_PATH,
    package_agentsec_pilot,
)


OUTPUT_DIR = Path("public_launch") / "roe8"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE8_AGENTSEC_PILOT_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE8_AGENTSEC_PILOT_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE8_NEXT_ACTIONS.md"

RISKY_PATTERNS = [
    ("overclaim", re.compile(r"\bverified\s+capability\b", re.I)),
    ("overclaim", re.compile(r"\bsafe\s+tool\b", re.I)),
    ("overclaim", re.compile(r"\bsecurity\s+certified\b", re.I)),
    ("overclaim", re.compile(r"\bquality\s+guaranteed\b", re.I)),
    ("overclaim", re.compile(r"\bproduction\s+ready\b", re.I)),
    ("overclaim", re.compile(r"\bcompliance\s+certified\b", re.I)),
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
    return f"""# ROE-8 AgentSec Pilot Summary

Gate decision: `{gate['decision']}`

Pilot: `{receipt.get('pilot_id', 'unknown')}`

| Field | Value |
| --- | --- |
| ALLOW | `{summary.get('allow_count', 0)}` |
| HOLD | `{summary.get('hold_count', 0)}` |
| BLOCK | `{summary.get('block_count', 0)}` |
| Redaction | `{gate['redaction_decision']}` |
| Live MCP call | `False` |
| External tool execution | `False` |
| GitHub API call | `False` |

This is a local/offline pilot receipt bundle. It is not security certification, not a compliance audit, not a quality guarantee, not product-readiness proof, and not action authorization.
"""


def build_next_actions_markdown(gate: dict[str, Any]) -> str:
    if gate["decision"] == "PASS_FIRST_AGENTSEC_PILOT_RECEIPT_READY":
        next_action = "Use the receipt as a sample bundle, then collect an owner-consented real pilot receipt before second-run decisions."
    else:
        next_action = "Resolve ROE-8 HOLD/BLOCK items before sharing the pilot receipt bundle."
    return f"""# ROE-8 Next Actions

Decision: `{gate['decision']}`

Recommended next action: {next_action}

Do not post comments, call GitHub APIs, run live MCP servers, execute external tools, request tokens, store partner secrets, or treat this receipt as certification.
"""


def run_roe8_gate(write_result: bool = True, ensure_sample: bool = True) -> dict[str, Any]:
    if ensure_sample and not (_repo_root() / RECEIPT_PATH).exists():
        package_agentsec_pilot(sample=True)

    receipt = _read_json(RECEIPT_PATH)
    redaction = _read_json(REDACTION_REPORT_PATH)
    memory = _read_json(FEEDBACK_MEMORY_PATH)
    artifacts = [
        _artifact_record(RECEIPT_PATH, "pilot_receipt"),
        _artifact_record(REVIEWER_READOUT_PATH, "reviewer_readout"),
        _artifact_record(REDACTION_REPORT_PATH, "redaction_report"),
        _artifact_record(FEEDBACK_MEMORY_PATH, "feedback_memory_entry"),
        _artifact_record(KNOWN_LIMITS_PATH, "known_limits"),
    ]
    missing = [item["path"] for item in artifacts if not item["exists"]]
    claim_findings = _scan_claims([RECEIPT_PATH, REVIEWER_READOUT_PATH, FEEDBACK_MEMORY_PATH, KNOWN_LIMITS_PATH])
    external_flags = {
        "external_actions_performed": bool(receipt.get("external_actions_performed", False)),
        "workflow_enabled": bool(receipt.get("workflow_enabled", False)),
        "github_api_used": bool(receipt.get("github_api_used", False)),
        "live_mcp_called": bool(receipt.get("live_mcp_called", False)),
        "external_tool_executed": bool(receipt.get("external_tool_executed", False)),
    }

    if any(external_flags.values()):
        decision = "BLOCK_EXTERNAL_ACTION"
    elif missing:
        decision = "HOLD_MISSING_READOUT"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT":
        decision = "BLOCK_SECRET_FINDING"
    elif redaction.get("decision") == "HOLD_REVIEW_RECOMMENDED":
        decision = "HOLD_REDACTION_REVIEW"
    elif claim_findings:
        finding_types = {finding["finding_type"] for finding in claim_findings}
        decision = "BLOCK_PRIVATE_KERNEL_EXPOSED" if "private_kernel" in finding_types else "BLOCK_OVERCLAIM"
    else:
        decision = "PASS_FIRST_AGENTSEC_PILOT_RECEIPT_READY"

    result = {
        "schema": "ResidualOps_ROE8AgentSecPilotGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "pilot_id": receipt.get("pilot_id", ""),
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
        "can_certify_security": False,
        "can_certify_quality": False,
        "can_prove_readiness": False,
        "can_authorize_action": False,
    }
    if write_result:
        _write_json(GATE_RESULT_PATH, result)
        _write_text(SUMMARY_PATH, build_summary_markdown(receipt, result))
        _write_text(NEXT_ACTIONS_PATH, build_next_actions_markdown(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-8 AgentSec pilot receipt gate.")
    parser.add_argument("--no-sample", action="store_true", help="Do not generate the sample receipt before gating.")
    parser.add_argument("--no-write", action="store_true", help="Run gate without writing public outputs.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe8_gate(write_result=not args.no_write, ensure_sample=not args.no_sample)
    print(f"roe8_agentsec_pilot_gate: {result['decision']} redaction={result['redaction_decision']}")


if __name__ == "__main__":
    main()
