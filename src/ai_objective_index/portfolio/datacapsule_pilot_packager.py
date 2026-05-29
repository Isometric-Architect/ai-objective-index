from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .datacapsule_eval_leakage import build_eval_leakage_summary
from .datacapsule_manifest_summary import build_corpus_manifest, load_manifest_payload
from .datacapsule_pilot_feedback_memory import build_feedback_memory_entry
from .datacapsule_pilot_receipt import (
    DataCapsuleFindingCard,
    DataCapsulePilotReceipt,
    DataCapsuleReceiptFeedbackMemory,
    DecisionSummary,
    datacapsule_must_not_claim,
    to_jsonable,
)
from .datacapsule_pilot_redaction import scan_payload
from .datacapsule_privacy_risk import build_privacy_risk_summary
from .datacapsule_reviewer_readout import build_reviewer_readout_markdown
from .datacapsule_source_rights import build_source_rights_summary
from .datacapsule_staleness_risk import summarize_staleness_risk
from .datacapsule_use_boundary import build_use_boundary


OUTPUT_DIR = Path("pilot_receipts") / "datacapsule"
MANIFEST_PATH = OUTPUT_DIR / "DATACAPSULE_CORPUS_MANIFEST_SAMPLE.json"
SOURCE_RIGHTS_PATH = OUTPUT_DIR / "DATACAPSULE_SOURCE_RIGHTS_SUMMARY_SAMPLE.json"
PRIVACY_RISK_PATH = OUTPUT_DIR / "DATACAPSULE_PRIVACY_RISK_SUMMARY_SAMPLE.json"
EVAL_LEAKAGE_PATH = OUTPUT_DIR / "DATACAPSULE_EVAL_LEAKAGE_SUMMARY_SAMPLE.json"
USE_BOUNDARY_PATH = OUTPUT_DIR / "DATACAPSULE_USE_BOUNDARY_SAMPLE.json"
RECEIPT_PATH = OUTPUT_DIR / "DATACAPSULE_PILOT_RECEIPT_SAMPLE.json"
REVIEWER_READOUT_PATH = OUTPUT_DIR / "DATACAPSULE_REVIEWER_READOUT.md"
FEEDBACK_MEMORY_PATH = OUTPUT_DIR / "DATACAPSULE_PILOT_FEEDBACK_MEMORY_ENTRY.json"
REDACTION_REPORT_PATH = OUTPUT_DIR / "DATACAPSULE_PILOT_REDACTION_REPORT.json"
KNOWN_LIMITS_PATH = OUTPUT_DIR / "DATACAPSULE_PILOT_KNOWN_LIMITS.md"


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


def _finding_cards(
    rights: dict[str, Any],
    privacy: dict[str, Any],
    eval_summary: dict[str, Any],
    boundary: dict[str, Any],
    staleness: dict[str, Any],
) -> list[DataCapsuleFindingCard]:
    findings = [
        DataCapsuleFindingCard(
            finding_id="datacapsule-pilot-finding-1",
            severity="info",
            decision="ALLOW",
            category="retrieve_boundary",
            evidence_ref="corpus_manifest#declared_allowed_uses",
            explanation="Manifest review artifact can record declared retrieval use as a local metadata signal.",
            next_action="keep as manifest-only review evidence",
            must_not_claim=datacapsule_must_not_claim(),
        )
    ]
    hold_reasons = []
    for summary, field in [(rights, "rights_status"), (privacy, "privacy_status"), (eval_summary, "leakage_status"), (staleness, "status")]:
        status = str(summary.get(field, ""))
        if status.startswith("HOLD"):
            hold_reasons.extend(summary.get("warnings", []) or [status])
    if hold_reasons:
        findings.append(
            DataCapsuleFindingCard(
                finding_id="datacapsule-pilot-finding-2",
                severity="medium",
                decision="HOLD",
                category="license_gap",
                evidence_ref="corpus_manifest#missing_fields",
                explanation="Manifest metadata has rights, privacy, evaluation-boundary, or staleness gaps.",
                next_action="request license, terms, privacy, consent, split-policy, and update-date evidence",
                must_not_claim=datacapsule_must_not_claim(),
            )
        )
    if "act" in boundary.get("blocked_uses", []) or "share" in boundary.get("blocked_uses", []) or "commercial" in boundary.get("blocked_uses", []):
        findings.append(
            DataCapsuleFindingCard(
                finding_id="datacapsule-pilot-finding-3",
                severity="high",
                decision="BLOCK",
                category="act_boundary",
                evidence_ref="use_boundary#blocked_uses",
                explanation="Action use is blocked and declared disallowed uses cannot be upgraded by a manifest-only pilot.",
                next_action="keep action use blocked unless separately authorized by a future owner-approved process",
                must_not_claim=datacapsule_must_not_claim(),
            )
        )
    return findings


def _decision_summary(findings: list[DataCapsuleFindingCard]) -> DecisionSummary:
    counts = Counter(finding.decision for finding in findings)
    return DecisionSummary(
        allow_count=counts["ALLOW"],
        hold_count=counts["HOLD"],
        block_count=counts["BLOCK"],
        top_hold_reasons=[finding.explanation for finding in findings if finding.decision == "HOLD"][:10],
        top_block_reasons=[finding.explanation for finding in findings if finding.decision == "BLOCK"][:10],
    )


def _capsule_decision(findings: list[DataCapsuleFindingCard]) -> str:
    categories = {finding.category for finding in findings if finding.decision == "BLOCK"}
    if "privacy_risk" in categories:
        return "BLOCK_SENSITIVE_DATA"
    if categories:
        return "BLOCK_ACTION_USE"
    if any(finding.category in {"license_gap", "source_rights"} and finding.decision == "HOLD" for finding in findings):
        return "HOLD_RIGHTS_REVIEW"
    if any(finding.category == "privacy_risk" and finding.decision == "HOLD" for finding in findings):
        return "HOLD_PRIVACY_REVIEW"
    if any(finding.category == "eval_leakage" and finding.decision == "HOLD" for finding in findings):
        return "HOLD_EVAL_LEAKAGE_REVIEW"
    return "ALLOW_MANIFEST_REVIEW_ARTIFACT"


def build_datacapsule_pilot_receipt(sample: bool = True, input_path: Path | None = None) -> DataCapsulePilotReceipt:
    payload = load_manifest_payload(None if sample else input_path)
    owner_status = "sample_fixture" if sample or input_path is None else "unknown"
    manifest = build_corpus_manifest(payload, owner_status=owner_status)
    rights = build_source_rights_summary(manifest)
    privacy = build_privacy_risk_summary(manifest)
    eval_summary = build_eval_leakage_summary(manifest)
    boundary = build_use_boundary(manifest, rights, privacy, eval_summary)
    staleness = summarize_staleness_risk(manifest)
    findings = _finding_cards(
        rights.model_dump(mode="json", by_alias=True),
        privacy.model_dump(mode="json", by_alias=True),
        eval_summary.model_dump(mode="json", by_alias=True),
        boundary.model_dump(mode="json", by_alias=True),
        staleness,
    )
    summary = _decision_summary(findings)
    pilot_hash = _stable_hash({"manifest": manifest.model_dump(mode="json", by_alias=True), "boundary": boundary.model_dump(mode="json", by_alias=True)})[:12]
    return DataCapsulePilotReceipt(
        pilot_id=f"datacapsule-pilot-{pilot_hash}",
        corpus_manifest=manifest,
        source_rights_summary=rights,
        privacy_risk_summary=privacy,
        eval_leakage_summary=eval_summary,
        use_boundary=boundary,
        decision_summary=summary,
        findings=findings,
        capsule_decision=_capsule_decision(findings),  # type: ignore[arg-type]
        feedback_memory=DataCapsuleReceiptFeedbackMemory(
            entry_id=f"datacapsule-feedback-{pilot_hash}",
            suggested_next_review="review HOLD/BLOCK findings before any owner-consented second DataCapsule pilot run",
            unresolved_questions=summary.top_hold_reasons[:5] + summary.top_block_reasons[:5],
            known_limits=[
                "local/offline manifest review only",
                "raw content not inspected",
                "no crawling or URL fetching",
                "no upload or model training",
                "not legal opinion",
                "not privacy audit",
                "not license clearance",
                "not evaluation-cleanliness proof",
                "no training or action authorization",
            ],
        ),
    )


def known_limits_markdown() -> str:
    return """# DataCapsule Pilot Known Limits

- Local/offline manifest metadata review only.
- Raw corpus content is not inspected.
- No crawling, scraping, URL fetching, data upload, model training, external API calls, or GitHub API calls.
- Not a legal opinion.
- Not a privacy audit.
- Not license clearance.
- Not evaluation-cleanliness proof.
- Not a data quality guarantee.
- No training authorization.
- No action authorization.
"""


def package_datacapsule_pilot(sample: bool = True, input_path: Path | None = None) -> dict[str, Any]:
    receipt = build_datacapsule_pilot_receipt(sample=sample, input_path=input_path)
    receipt_payload = to_jsonable(receipt)
    manifest_payload = receipt.corpus_manifest.model_dump(mode="json", by_alias=True)
    rights_payload = receipt.source_rights_summary.model_dump(mode="json", by_alias=True)
    privacy_payload = receipt.privacy_risk_summary.model_dump(mode="json", by_alias=True)
    eval_payload = receipt.eval_leakage_summary.model_dump(mode="json", by_alias=True)
    boundary_payload = receipt.use_boundary.model_dump(mode="json", by_alias=True)
    redaction = scan_payload(receipt_payload, "datacapsule-pilot-receipt")
    memory_entry = build_feedback_memory_entry(receipt_payload).model_dump(mode="json", by_alias=True)

    _write_json(MANIFEST_PATH, manifest_payload)
    _write_json(SOURCE_RIGHTS_PATH, rights_payload)
    _write_json(PRIVACY_RISK_PATH, privacy_payload)
    _write_json(EVAL_LEAKAGE_PATH, eval_payload)
    _write_json(USE_BOUNDARY_PATH, boundary_payload)
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
            "manifest": str(MANIFEST_PATH).replace("\\", "/"),
            "source_rights": str(SOURCE_RIGHTS_PATH).replace("\\", "/"),
            "privacy_risk": str(PRIVACY_RISK_PATH).replace("\\", "/"),
            "eval_leakage": str(EVAL_LEAKAGE_PATH).replace("\\", "/"),
            "use_boundary": str(USE_BOUNDARY_PATH).replace("\\", "/"),
            "receipt": str(RECEIPT_PATH).replace("\\", "/"),
            "reviewer_readout": str(REVIEWER_READOUT_PATH).replace("\\", "/"),
            "redaction_report": str(REDACTION_REPORT_PATH).replace("\\", "/"),
            "feedback_memory_entry": str(FEEDBACK_MEMORY_PATH).replace("\\", "/"),
            "known_limits": str(KNOWN_LIMITS_PATH).replace("\\", "/"),
        },
        "raw_content_inspected": False,
        "external_network_used": False,
        "crawler_used": False,
        "data_uploaded": False,
        "model_trained": False,
        "external_api_used": False,
        "github_api_used": False,
        "token_printed": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package a local/offline DataCapsule pilot receipt bundle.")
    parser.add_argument("--sample", action="store_true", help="Use the public-safe DataCapsule sample manifest fixture.")
    parser.add_argument("--input", type=Path, help="Local JSON corpus manifest file.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = package_datacapsule_pilot(sample=args.sample or args.input is None, input_path=args.input)
    receipt = result["receipt"]
    summary = receipt["decision_summary"]
    print(
        "datacapsule_pilot_packager: "
        f"{result['redaction']['decision']} pilot={receipt['pilot_id']} "
        f"allow={summary['allow_count']} hold={summary['hold_count']} block={summary['block_count']}"
    )


if __name__ == "__main__":
    main()
