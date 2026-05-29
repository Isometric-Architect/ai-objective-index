from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .qira_behavior_contract import behavior_contract_detects_forbidden, build_behavior_contract
from .qira_ci_evidence_summary import build_ci_evidence_summary
from .qira_patch_classifier import SAMPLE_PATCH_DIFF, classify_qira_patch, stable_id
from .qira_pilot_feedback_memory import build_feedback_memory_entry
from .qira_pilot_receipt import (
    DecisionSummary,
    OwnerConsent,
    QIRAFindingCard,
    QIRAPilotReceipt,
    QIRAReceiptFeedbackMemory,
    QIRATaskPacket,
    qira_must_not_claim,
    to_jsonable,
)
from .qira_pilot_redaction import scan_payload
from .qira_reviewer_readout import build_reviewer_readout_markdown


OUTPUT_DIR = Path("pilot_receipts") / "qira"
TASK_PACKET_PATH = OUTPUT_DIR / "QIRA_TASK_PACKET_SAMPLE.json"
PATCH_CLASSIFICATION_PATH = OUTPUT_DIR / "QIRA_PATCH_CLASSIFICATION_SAMPLE.json"
BEHAVIOR_CONTRACT_PATH = OUTPUT_DIR / "QIRA_BEHAVIOR_CONTRACT_SAMPLE.json"
CI_EVIDENCE_PATH = OUTPUT_DIR / "QIRA_CI_EVIDENCE_SUMMARY_SAMPLE.json"
RECEIPT_PATH = OUTPUT_DIR / "QIRA_PILOT_RECEIPT_SAMPLE.json"
REVIEWER_READOUT_PATH = OUTPUT_DIR / "QIRA_REVIEWER_READOUT.md"
FEEDBACK_MEMORY_PATH = OUTPUT_DIR / "QIRA_PILOT_FEEDBACK_MEMORY_ENTRY.json"
REDACTION_REPORT_PATH = OUTPUT_DIR / "QIRA_PILOT_REDACTION_REPORT.json"
KNOWN_LIMITS_PATH = OUTPUT_DIR / "QIRA_PILOT_KNOWN_LIMITS.md"


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


def build_sample_task_packet(input_source: str = "sample_patch") -> QIRATaskPacket:
    task_id = stable_id("qira-task", "sample", input_source)
    return QIRATaskPacket(
        task_id=task_id,
        task_title="Package a local QIRA pilot release-gate review.",
        task_goal="Review a local patch fixture through task packet, patch classification, behavior contract, CI evidence summary, reviewer readout, receipt, and feedback memory.",
        repo_label="sample/local fixture repository",
        owner_consent=OwnerConsent(status="sample_fixture", evidence_note="sample fixture only; no external repository owner contacted"),
        input_source=input_source,  # type: ignore[arg-type]
        intended_change_type="tests",
    )


def _findings_for_sample(
    classification: dict[str, Any],
    ci_summary: dict[str, Any],
    contract_forbidden: bool,
) -> list[QIRAFindingCard]:
    findings = [
        QIRAFindingCard(
            finding_id="qira-pilot-finding-1",
            severity="info",
            decision="ALLOW",
            category="patch_scope",
            evidence_ref="sample_patch#docs-tests",
            explanation="Docs/test fixture review can be represented as a local reviewer artifact.",
            next_action="keep as local review evidence only",
            must_not_claim=qira_must_not_claim(),
        )
    ]
    missing = ci_summary.get("missing_evidence", []) if isinstance(ci_summary.get("missing_evidence"), list) else []
    if missing:
        findings.append(
            QIRAFindingCard(
                finding_id="qira-pilot-finding-2",
                severity="medium",
                decision="HOLD",
                category="ci_evidence_gap",
                evidence_ref=str(ci_summary.get("ci_evidence_id", "qira-ci-summary")),
                explanation="CI evidence is partial or generated sample metadata; independent CI evidence is still needed.",
                next_action="request owner-provided or copied CI summary before second-run readout",
                must_not_claim=qira_must_not_claim(),
            )
        )
    if classification.get("classification_decision") == "BLOCK_FORBIDDEN_ACTION" or contract_forbidden:
        findings.append(
            QIRAFindingCard(
                finding_id="qira-pilot-finding-3",
                severity="high",
                decision="BLOCK",
                category="release_side_effect",
                evidence_ref="sample_patch#negative-control-deploy",
                explanation="Negative-control fixture includes release/deploy language that a local QIRA pilot cannot authorize.",
                next_action="remove release/deploy side effect or route to a separate owner-approved release gate",
                must_not_claim=qira_must_not_claim(),
            )
        )
    return findings


def _decision_summary(findings: list[QIRAFindingCard]) -> DecisionSummary:
    counts = Counter(finding.decision for finding in findings)
    return DecisionSummary(
        allow_count=counts["ALLOW"],
        hold_count=counts["HOLD"],
        block_count=counts["BLOCK"],
        top_hold_reasons=[finding.explanation for finding in findings if finding.decision == "HOLD"][:10],
        top_block_reasons=[finding.explanation for finding in findings if finding.decision == "BLOCK"][:10],
    )


def _release_gate_decision(findings: list[QIRAFindingCard]) -> str:
    if any(finding.category == "secret_risk" and finding.decision == "BLOCK" for finding in findings):
        return "BLOCK_SECRET_RISK"
    if any(finding.category in {"external_action_risk", "release_side_effect"} and finding.decision == "BLOCK" for finding in findings):
        return "BLOCK_RELEASE_SIDE_EFFECT"
    if any(finding.decision == "BLOCK" for finding in findings):
        return "BLOCK_EXTERNAL_ACTION"
    if any(finding.category == "ci_evidence_gap" and finding.decision == "HOLD" for finding in findings):
        return "HOLD_TEST_EVIDENCE"
    if any(finding.decision == "HOLD" for finding in findings):
        return "HOLD_OWNER_REVIEW"
    return "ALLOW_REVIEW_ARTIFACT"


def build_qira_pilot_receipt(sample: bool = True, input_path: Path | None = None) -> QIRAPilotReceipt:
    if sample or input_path is None:
        patch_text = SAMPLE_PATCH_DIFF
        task = build_sample_task_packet("sample_patch")
    else:
        patch_text = input_path.read_text(encoding="utf-8", errors="ignore")
        task = build_sample_task_packet("local_patch")
        task = task.model_copy(
            update={
                "repo_label": f"local file: {input_path.name}",
                "owner_consent": OwnerConsent(status="unknown", evidence_note="local input supplied; owner consent not asserted by QIRA"),
            }
        )
    classification = classify_qira_patch(task.task_id, patch_text=patch_text)
    contract = build_behavior_contract(task)
    contract_forbidden = behavior_contract_detects_forbidden(contract, patch_text, [])
    ci_summary = build_ci_evidence_summary(task.task_id)
    findings = _findings_for_sample(classification.model_dump(mode="json", by_alias=True), ci_summary.model_dump(mode="json", by_alias=True), contract_forbidden)
    summary = _decision_summary(findings)
    pilot_hash = _stable_hash(
        {
            "task": task.model_dump(mode="json", by_alias=True),
            "classification": classification.model_dump(mode="json", by_alias=True),
            "ci": ci_summary.model_dump(mode="json", by_alias=True),
        }
    )[:12]
    return QIRAPilotReceipt(
        pilot_id=f"qira-pilot-{pilot_hash}",
        task_packet=task,
        patch_classification=classification,
        behavior_contract=contract,
        ci_evidence_summary=ci_summary,
        decision_summary=summary,
        findings=findings,
        release_gate_decision=_release_gate_decision(findings),  # type: ignore[arg-type]
        feedback_memory=QIRAReceiptFeedbackMemory(
            entry_id=f"qira-feedback-{pilot_hash}",
            suggested_next_review="review HOLD/BLOCK findings before any second owner-consented QIRA pilot run",
            unresolved_questions=summary.top_hold_reasons[:5] + summary.top_block_reasons[:5],
            known_limits=[
                "local/offline patch review only",
                "no GitHub API call",
                "no external repository mutation",
                "not code correctness proof",
                "not security certification",
                "not quality guarantee",
                "no merge or deploy authorization",
            ],
        ),
    )


def known_limits_markdown() -> str:
    return """# QIRA Pilot Known Limits

- Local/offline code-change review artifact only.
- No GitHub API calls.
- No external repository mutation.
- No PR comments, issues, branches, merges, deploys, or package publishing.
- No arbitrary external command execution.
- Not code correctness proof.
- Not security certification.
- Not a quality guarantee.
- Not merge or deploy authorization.
"""


def package_qira_pilot(sample: bool = True, input_path: Path | None = None) -> dict[str, Any]:
    receipt = build_qira_pilot_receipt(sample=sample, input_path=input_path)
    receipt_payload = to_jsonable(receipt)
    task_payload = receipt.task_packet.model_dump(mode="json", by_alias=True)
    classification_payload = receipt.patch_classification.model_dump(mode="json", by_alias=True)
    contract_payload = receipt.behavior_contract.model_dump(mode="json", by_alias=True)
    ci_payload = receipt.ci_evidence_summary.model_dump(mode="json", by_alias=True)
    redaction = scan_payload(receipt_payload, "qira-pilot-receipt")
    memory_entry = build_feedback_memory_entry(receipt_payload).model_dump(mode="json", by_alias=True)

    _write_json(TASK_PACKET_PATH, task_payload)
    _write_json(PATCH_CLASSIFICATION_PATH, classification_payload)
    _write_json(BEHAVIOR_CONTRACT_PATH, contract_payload)
    _write_json(CI_EVIDENCE_PATH, ci_payload)
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
            "task_packet": str(TASK_PACKET_PATH).replace("\\", "/"),
            "patch_classification": str(PATCH_CLASSIFICATION_PATH).replace("\\", "/"),
            "behavior_contract": str(BEHAVIOR_CONTRACT_PATH).replace("\\", "/"),
            "ci_evidence_summary": str(CI_EVIDENCE_PATH).replace("\\", "/"),
            "receipt": str(RECEIPT_PATH).replace("\\", "/"),
            "reviewer_readout": str(REVIEWER_READOUT_PATH).replace("\\", "/"),
            "redaction_report": str(REDACTION_REPORT_PATH).replace("\\", "/"),
            "feedback_memory_entry": str(FEEDBACK_MEMORY_PATH).replace("\\", "/"),
            "known_limits": str(KNOWN_LIMITS_PATH).replace("\\", "/"),
        },
        "github_api_used": False,
        "external_repo_modified": False,
        "external_actions_performed": False,
        "merge_performed": False,
        "deploy_performed": False,
        "token_printed": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package a local/offline QIRA pilot receipt bundle.")
    parser.add_argument("--sample", action="store_true", help="Use the public-safe QIRA sample patch fixture.")
    parser.add_argument("--input", type=Path, help="Local patch or diff file.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = package_qira_pilot(sample=args.sample or args.input is None, input_path=args.input)
    receipt = result["receipt"]
    summary = receipt["decision_summary"]
    print(
        "qira_pilot_packager: "
        f"{result['redaction']['decision']} pilot={receipt['pilot_id']} "
        f"allow={summary['allow_count']} hold={summary['hold_count']} block={summary['block_count']}"
    )


if __name__ == "__main__":
    main()
