from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from ai_objective_index.agentsec.policy_gate import SAMPLE_MANIFEST_SET, build_policy_gate_result, read_manifest_set
from ai_objective_index.real_pypi_upload_gate import _repo_root

from .agentsec_pilot_feedback_memory import build_feedback_memory_entry
from .agentsec_pilot_readout import build_reviewer_readout_markdown
from .agentsec_pilot_receipt import (
    AgentSecPilotReceipt,
    DecisionSummary,
    FindingCard,
    InputManifest,
    OwnerConsent,
    PacketSummary,
    ReceiptFeedbackMemory,
    must_not_claim,
    receipt_to_jsonable,
)
from .agentsec_pilot_redaction import scan_payload


OUTPUT_DIR = Path("pilot_receipts") / "agentsec"
RECEIPT_PATH = OUTPUT_DIR / "AGENTSEC_PILOT_RECEIPT_SAMPLE.json"
REVIEWER_READOUT_PATH = OUTPUT_DIR / "AGENTSEC_PILOT_REVIEWER_READOUT.md"
FEEDBACK_MEMORY_PATH = OUTPUT_DIR / "AGENTSEC_PILOT_FEEDBACK_MEMORY_ENTRY.json"
REDACTION_REPORT_PATH = OUTPUT_DIR / "AGENTSEC_PILOT_REDACTION_REPORT.json"
KNOWN_LIMITS_PATH = OUTPUT_DIR / "AGENTSEC_PILOT_KNOWN_LIMITS.md"


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


def _stable_hash(payload: Any) -> str:
    text = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _decision_bucket(value: str) -> str:
    if value.startswith("ALLOW"):
        return "ALLOW"
    if value.startswith("BLOCK"):
        return "BLOCK"
    return "HOLD"


def _category_for_packet(packet: dict[str, Any]) -> str:
    if packet.get("forbidden_action_findings"):
        return "forbidden_action"
    if packet.get("unsupported_claim_findings"):
        return "unsupported_claim"
    if packet.get("hidden_instruction_findings"):
        return "hidden_instruction"
    if packet.get("namespace_findings"):
        return "namespace_lookalike"
    permission_scope = packet.get("permission_scope", {}) if isinstance(packet.get("permission_scope"), dict) else {}
    if any(permission_scope.get(field) for field in ["network_access", "file_access", "write_access", "secret_access", "browser_access", "code_execution"]):
        return "permission_scope"
    return "unknown"


def _severity_for_decision(decision: str, category: str) -> str:
    if decision == "BLOCK":
        return "high"
    if category in {"hidden_instruction", "permission_scope", "namespace_lookalike"}:
        return "medium"
    if decision == "HOLD":
        return "low"
    return "info"


def _finding_explanation(packet: dict[str, Any]) -> str:
    notes = packet.get("residual_notes") if isinstance(packet.get("residual_notes"), list) else []
    if notes:
        return str(notes[0])
    return "Local manifest metadata reviewed under AgentSec public-safe policy."


def build_receipt_from_policy_gate(
    policy_gate: dict[str, Any],
    source_type: str = "fixture",
    path_or_id: str = "agentsec-sample-fixture",
    project_label: str = "AgentSec sample pilot",
    owner_status: str = "sample_fixture",
) -> AgentSecPilotReceipt:
    packets = policy_gate.get("packets") if isinstance(policy_gate.get("packets"), list) else []
    findings: list[FindingCard] = []
    decision_counts: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    permission_count = 0
    hidden_count = 0
    namespace_count = 0
    unsupported_count = 0
    forbidden_count = 0
    for index, packet in enumerate(packets, start=1):
        if not isinstance(packet, dict):
            continue
        raw_decision = str(packet.get("risk_decision", "HOLD_REVIEW_REQUIRED"))
        decision = _decision_bucket(raw_decision)
        decision_counts[decision] += 1
        category = _category_for_packet(packet)
        categories[category] += 1
        permission_scope = packet.get("permission_scope", {}) if isinstance(packet.get("permission_scope"), dict) else {}
        permission_count += sum(
            1
            for field in ["network_access", "file_access", "write_access", "secret_access", "browser_access", "code_execution"]
            if permission_scope.get(field)
        )
        hidden_count += len(packet.get("hidden_instruction_findings") or [])
        namespace_count += len(packet.get("namespace_findings") or [])
        unsupported_count += len(packet.get("unsupported_claim_findings") or [])
        forbidden_count += len(packet.get("forbidden_action_findings") or [])
        next_action = "review metadata before use" if decision == "HOLD" else "remove or justify blocked manifest language" if decision == "BLOCK" else "keep as metadata-only candidate"
        findings.append(
            FindingCard(
                finding_id=f"agentsec-pilot-finding-{index}",
                severity=_severity_for_decision(decision, category),  # type: ignore[arg-type]
                decision=decision,  # type: ignore[arg-type]
                category=category,  # type: ignore[arg-type]
                evidence_ref=str(packet.get("manifest_path", path_or_id)),
                explanation=_finding_explanation(packet),
                next_action=next_action,
                must_not_claim=must_not_claim(),
            )
        )

    hold_reasons = [str(item) for item in policy_gate.get("policy_hold_reasons", []) if str(item).strip()]
    block_reasons = [str(item) for item in policy_gate.get("policy_block_reasons", []) if str(item).strip()]
    pilot_hash = _stable_hash({"path_or_id": path_or_id, "policy_gate": policy_gate})[:12]
    return AgentSecPilotReceipt(
        pilot_id=f"agentsec-pilot-{pilot_hash}",
        project_label=project_label,
        owner_consent=OwnerConsent(status=owner_status, evidence_note="sample/local owner consent metadata only"),
        input_manifest=InputManifest(source_type=source_type, path_or_id=path_or_id, hash=_stable_hash(policy_gate)),
        packet_summary=PacketSummary(
            manifest_count=int(policy_gate.get("packet_count") or len(packets)),
            tool_count=len(packets),
            permission_count=permission_count,
            hidden_instruction_findings=hidden_count,
            namespace_findings=namespace_count,
            unsupported_claim_findings=unsupported_count,
            forbidden_action_findings=forbidden_count,
        ),
        decision_summary=DecisionSummary(
            allow_count=decision_counts["ALLOW"],
            hold_count=decision_counts["HOLD"],
            block_count=decision_counts["BLOCK"],
            top_hold_reasons=hold_reasons[:10],
            top_block_reasons=block_reasons[:10],
        ),
        findings=findings,
        feedback_memory=ReceiptFeedbackMemory(
            entry_id=f"agentsec-feedback-{pilot_hash}",
            suggested_next_review="review HOLD/BLOCK findings before any second owner-consented pilot run",
            unresolved_questions=hold_reasons[:5] + block_reasons[:5],
            known_limits=[
                "local/offline manifest review only",
                "no live MCP call",
                "no external tool execution",
                "not security certification",
                "not quality guarantee",
                "not compliance audit",
                "not action authorization",
            ],
        ),
    )


def known_limits_markdown() -> str:
    return """# AgentSec Pilot Known Limits

- Local/offline manifest review only.
- No live MCP server calls.
- No external tool execution.
- No GitHub API calls or PR comments.
- No external repository modification.
- Not security certification.
- Not compliance audit.
- Not a quality guarantee.
- Not production-readiness proof.
- Not action authorization.
"""


def package_agentsec_pilot(sample: bool = True, input_path: Path | None = None) -> dict[str, Any]:
    if sample or input_path is None:
        payloads = SAMPLE_MANIFEST_SET
        source_type = "fixture"
        path_or_id = "agentsec-public-safe-sample-fixture"
        project_label = "AgentSec sample pilot"
        owner_status = "sample_fixture"
    else:
        payloads = read_manifest_set(input_path)
        source_type = "local_file"
        path_or_id = str(input_path).replace("\\", "/")
        project_label = f"AgentSec local pilot for {input_path.name}"
        owner_status = "unknown"
    policy_gate = build_policy_gate_result(payloads, manifest_set_path=path_or_id)
    policy_payload = policy_gate.model_dump(mode="json", by_alias=True)
    receipt = build_receipt_from_policy_gate(policy_payload, source_type, path_or_id, project_label, owner_status)
    receipt_payload = receipt_to_jsonable(receipt)
    redaction = scan_payload(receipt_payload, "agentsec-pilot-receipt")
    memory_entry = build_feedback_memory_entry(receipt_payload).model_dump(mode="json", by_alias=True)
    _write_json(RECEIPT_PATH, receipt_payload)
    _write_text(REVIEWER_READOUT_PATH, build_reviewer_readout_markdown(receipt_payload))
    _write_json(REDACTION_REPORT_PATH, redaction)
    _write_json(FEEDBACK_MEMORY_PATH, memory_entry)
    _write_text(KNOWN_LIMITS_PATH, known_limits_markdown())
    return {
        "receipt": receipt_payload,
        "redaction": redaction,
        "feedback_memory": memory_entry,
        "paths": {
            "receipt": str(RECEIPT_PATH).replace("\\", "/"),
            "reviewer_readout": str(REVIEWER_READOUT_PATH).replace("\\", "/"),
            "redaction_report": str(REDACTION_REPORT_PATH).replace("\\", "/"),
            "feedback_memory_entry": str(FEEDBACK_MEMORY_PATH).replace("\\", "/"),
            "known_limits": str(KNOWN_LIMITS_PATH).replace("\\", "/"),
        },
        "external_actions_performed": False,
        "live_mcp_called": False,
        "external_tool_executed": False,
        "github_api_used": False,
        "token_printed": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package a local/offline AgentSec pilot receipt bundle.")
    parser.add_argument("--sample", action="store_true", help="Use the public-safe AgentSec sample fixture.")
    parser.add_argument("--input", type=Path, help="Local JSON manifest file, list, or directory.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = package_agentsec_pilot(sample=args.sample or args.input is None, input_path=args.input)
    receipt = result["receipt"]
    print(
        "agentsec_pilot_packager: "
        f"{result['redaction']['decision']} pilot={receipt['pilot_id']} "
        f"hold={receipt['decision_summary']['hold_count']} block={receipt['decision_summary']['block_count']}"
    )


if __name__ == "__main__":
    main()
