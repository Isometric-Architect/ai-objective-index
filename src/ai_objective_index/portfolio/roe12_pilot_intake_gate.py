from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_intake_packager import (
    AGENTSEC_PACKET_PATH,
    AGENTSEC_ROUTE_PATH,
    CONSENT_TEMPLATE_PATH,
    DATACAPSULE_PACKET_PATH,
    DATACAPSULE_ROUTE_PATH,
    FEEDBACK_MEMORY_SAMPLE_PATH,
    INTAKE_FORM_TEMPLATE_PATH,
    KNOWN_LIMITS_PATH,
    QIRA_PACKET_PATH,
    QIRA_ROUTE_PATH,
    REDACTION_PATH,
    REVIEWER_INSTRUCTIONS_PATH,
    RUN_PLAN_PATH,
    package_pilot_intake,
)


OUTPUT_DIR = Path("public_launch") / "roe12"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE12_PILOT_INTAKE_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE12_PILOT_INTAKE_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE12_NEXT_ACTIONS.md"

RISKY_PATTERNS = [
    re.compile(r"\bsecurity\s+certification\b", re.I),
    re.compile(r"\bcorrectness\s+proof\b", re.I),
    re.compile(r"\blegal\s+clearance\b", re.I),
    re.compile(r"\bprivacy\s+clearance\b", re.I),
    re.compile(r"\blicense\s+clearance\b", re.I),
    re.compile(r"\beval[-\s]+clean\s+proof\b", re.I),
    re.compile(r"\bquality\s+guarantee\b", re.I),
    re.compile(r"\bproduct\s+readiness\b", re.I),
    re.compile(r"\bexternal\s+action\s+authorization\b", re.I),
]
SAFE_CONTEXT = ["not ", "no ", "do not", "does not", "cannot ", "without ", "must not", "known limits", "claim boundary", "consent does not"]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _exists(path: Path) -> bool:
    return (_repo_root() / path).exists()


def scan_intake_claims(paths: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        full = _repo_root() / path
        if not full.exists() or not full.is_file():
            continue
        lines = full.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            if any(marker in lowered for marker in SAFE_CONTEXT):
                continue
            previous = "\n".join(lines[max(0, line_number - 5) : line_number]).lower()
            if "what this is not" in previous or "must_not_claim" in previous or "claim boundary" in previous:
                continue
            for pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append({"path": str(path).replace("\\", "/"), "line": line_number, "pattern": pattern.pattern})
                    break
    return findings


def _summary_markdown(result: dict[str, Any]) -> str:
    return f"""# ROE-12 Pilot Intake Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Sample packets | `{result['sample_packet_count']}` |
| Routes ready | `{result['route_ready_count']}` |
| Redaction | `{result['redaction_decision']}` |
| Claim findings | `{result['claim_finding_count']}` |
| External action used | `{result['external_action_used']}` |

The kit is a local/offline intake and routing layer. It is not certification, proof, product readiness, quality guarantee, or action authorization.
"""


def _next_actions_markdown(result: dict[str, Any]) -> str:
    next_step = "ROE-13 First Owner-Consented Pilot Dry-Run" if result["decision"] == "PASS_OWNER_CONSENTED_PILOT_INTAKE_READY" else "resolve ROE-12 HOLD/BLOCK findings"
    return f"""# ROE-12 Next Actions

Decision: `{result['decision']}`

Recommended next step: {next_step}.

Keep the same limits: receive local files only, confirm owner consent, run redaction, route the vertical, produce local/offline receipts, and do not post, merge, deploy, upload, train, fetch, clone, call external APIs, use credentials, or make certification/proof/product-readiness claims.
"""


def run_roe12_gate(write_result: bool = True, ensure_packaged: bool = True) -> dict[str, Any]:
    packaged = package_pilot_intake(sample=True) if ensure_packaged else {}
    required = [
        AGENTSEC_PACKET_PATH,
        QIRA_PACKET_PATH,
        DATACAPSULE_PACKET_PATH,
        AGENTSEC_ROUTE_PATH,
        QIRA_ROUTE_PATH,
        DATACAPSULE_ROUTE_PATH,
        CONSENT_TEMPLATE_PATH,
        INTAKE_FORM_TEMPLATE_PATH,
        RUN_PLAN_PATH,
        REDACTION_PATH,
        REVIEWER_INSTRUCTIONS_PATH,
        KNOWN_LIMITS_PATH,
        FEEDBACK_MEMORY_SAMPLE_PATH,
    ]
    missing = [str(path).replace("\\", "/") for path in required if not _exists(path)]
    packets = [_read_json(path) for path in [AGENTSEC_PACKET_PATH, QIRA_PACKET_PATH, DATACAPSULE_PACKET_PATH]]
    routes = [_read_json(path) for path in [AGENTSEC_ROUTE_PATH, QIRA_ROUTE_PATH, DATACAPSULE_ROUTE_PATH]]
    redaction = packaged.get("redaction") if packaged else _read_json(REDACTION_PATH)
    claim_findings = scan_intake_claims(required + [Path("docs") / "portfolio" / "pilot_intake_claim_boundaries.md"])
    external_action_used = any(bool(packet.get("external_action_requested", False)) for packet in packets) or any(
        bool(packet.get("allowed_review_scope", {}).get(field, False))
        for packet in packets
        for field in ["external_network", "github_api_call", "live_tool_execution", "external_repo_mutation", "posting_or_commenting"]
    )
    private_kernel_exposed = bool(redaction.get("private_kernel_exposed", False))
    token_printed = any(bool(packet.get("token_printed", False)) for packet in packets) or bool(redaction.get("token_printed", False))
    route_ready_count = len([route for route in routes if route.get("can_generate_pilot_receipt") is True])

    if missing:
        decision = "HOLD_MISSING_CONSENT_TEMPLATE" if str(CONSENT_TEMPLATE_PATH).replace("\\", "/") in missing else "HOLD_MISSING_ROUTE"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT" or token_printed:
        decision = "BLOCK_SECRET_FINDING"
    elif redaction.get("decision") == "HOLD_REVIEW_RECOMMENDED":
        decision = "HOLD_REDACTION_REVIEW"
    elif claim_findings:
        decision = "BLOCK_OVERCLAIM"
    elif external_action_used:
        decision = "BLOCK_EXTERNAL_ACTION"
    elif private_kernel_exposed:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    elif route_ready_count < 3:
        decision = "HOLD_MISSING_ROUTE"
    else:
        decision = "PASS_OWNER_CONSENTED_PILOT_INTAKE_READY"

    result = {
        "schema": "ResidualOps_ROE12PilotIntakeGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "sample_packet_count": len([packet for packet in packets if packet]),
        "route_ready_count": route_ready_count,
        "routes": [
            {
                "intake_id": route.get("intake_id", ""),
                "selected_vertical": route.get("selected_vertical", ""),
                "can_generate_pilot_receipt": route.get("can_generate_pilot_receipt", False),
            }
            for route in routes
        ],
        "missing_artifacts": missing,
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "redaction_findings": redaction.get("finding_count", 0),
        "claim_finding_count": len(claim_findings),
        "claim_findings": claim_findings[:50],
        "external_action_used": external_action_used,
        "token_printed": token_printed,
        "private_kernel_exposed": private_kernel_exposed,
        "can_certify_security": False,
        "can_prove_code_correctness": False,
        "can_provide_legal_privacy_license_eval_proof": False,
        "can_claim_product_readiness": False,
        "can_authorize_external_action": False,
    }
    if write_result:
        _write_json(GATE_RESULT_PATH, result)
        _write_text(SUMMARY_PATH, _summary_markdown(result))
        _write_text(NEXT_ACTIONS_PATH, _next_actions_markdown(result))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ROE-12 owner-consented pilot intake gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-package", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe12_gate(write_result=not args.no_write, ensure_packaged=not args.no_package)
    print(
        "roe12_pilot_intake_gate: "
        f"{result['decision']} redaction={result['redaction_decision']} routes_ready={result['route_ready_count']}"
    )


if __name__ == "__main__":
    main()
