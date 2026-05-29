from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_feedback_packet import PilotFeedbackPacket, feedback_packet_to_jsonable, sample_feedback_packets
from .pilot_feedback_redaction import scan_feedback_payload


ClassificationDecision = Literal[
    "ACCEPT_AS_FIXTURE_CANDIDATE",
    "HOLD_NEEDS_MORE_CONTEXT",
    "HOLD_REDACTION_REVIEW",
    "HOLD_OWNER_CONFIRMATION",
    "HOLD_MANUAL_TRIAGE",
    "BLOCK_EXTERNAL_ACTION_REQUEST",
    "BLOCK_SECRET_OR_PRIVATE_DATA",
    "BLOCK_CERTIFICATION_CLAIM",
]
Severity = Literal["info", "low", "medium", "high", "critical", "unknown"]

OUTPUT_PATH = Path("pilot_feedback") / "PILOT_FEEDBACK_CLASSIFICATION_SAMPLE.json"

EXTERNAL_ACTION_PATTERNS = [
    re.compile(r"\b(create|open)\s+(?:a\s+)?(?:github\s+)?issue\b", re.I),
    re.compile(r"\b(comment|post)\s+(?:on\s+)?(?:a\s+)?pr\b", re.I),
    re.compile(r"\bmerge\b", re.I),
    re.compile(r"\bdeploy\b", re.I),
    re.compile(r"\bpublish\s+(?:package|release)\b", re.I),
    re.compile(r"\bclone\s+(?:the\s+)?repo\b", re.I),
    re.compile(r"\bfetch\s+url\b", re.I),
]
CERTIFICATION_PATTERNS = [
    re.compile(r"\bcertif(?:y|ication)\b", re.I),
    re.compile(r"\bprove\s+(?:it\s+is\s+)?(?:correct|safe|compliant)\b", re.I),
    re.compile(r"\bsay\s+(?:it\s+is\s+)?safe\b", re.I),
    re.compile(r"\blegal\s+clearance\b", re.I),
    re.compile(r"\bprivacy\s+clearance\b", re.I),
    re.compile(r"\blicense\s+clearance\b", re.I),
    re.compile(r"\bproduct\s+ready\b", re.I),
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class PilotFeedbackClassification(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_id: str = Field(default="ResidualOps_PilotFeedbackClassification/v0.1", alias="schema")
    classification_id: str
    feedback_id: str
    generated_at: str = Field(default_factory=timestamp)
    classification: ClassificationDecision
    issue_categories: list[str] = Field(default_factory=list)
    severity: Severity = "info"
    affected_verticals: list[str] = Field(default_factory=list)
    affected_receipts: list[str] = Field(default_factory=list)
    should_update_finding: bool = False
    should_update_claim_boundary: bool = False
    should_add_negative_control: bool = False
    should_add_fixture: bool = False
    should_request_evidence: bool = False
    should_run_second_pass: bool = False
    reason: str = ""
    next_actions: list[str] = Field(default_factory=list)
    can_certify_security: bool = False
    can_prove_correctness: bool = False
    can_authorize_external_action: bool = False


def _text_has(patterns: list[re.Pattern[str]], text: str) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def classify_feedback(packet: PilotFeedbackPacket) -> PilotFeedbackClassification:
    text = " ".join([packet.feedback_text, packet.requested_change, " ".join(packet.proposed_evidence_refs)]).strip()
    redaction = scan_feedback_payload(feedback_packet_to_jsonable(packet), label=packet.feedback_id)
    issue_categories = [packet.feedback_category]
    next_actions = [
        "keep feedback local",
        "preserve claim boundaries",
        "do not post, merge, deploy, publish, fetch, clone, upload, train, or call external APIs",
    ]

    if packet.external_action_requested or _text_has(EXTERNAL_ACTION_PATTERNS, text):
        return PilotFeedbackClassification(
            classification_id=f"classification-{packet.feedback_id}",
            feedback_id=packet.feedback_id,
            classification="BLOCK_EXTERNAL_ACTION_REQUEST",
            issue_categories=issue_categories + ["external_action_request"],
            severity="high",
            affected_verticals=[packet.vertical],
            affected_receipts=packet.affected_artifact_refs,
            reason="feedback requests an external action, which cannot be authorized by the feedback layer",
            next_actions=next_actions + ["remove external action request and provide a local artifact summary if a second pass is needed"],
        )
    if packet.contains_private_data_declared or redaction["decision"] == "BLOCK_SENSITIVE_CONTENT":
        return PilotFeedbackClassification(
            classification_id=f"classification-{packet.feedback_id}",
            feedback_id=packet.feedback_id,
            classification="BLOCK_SECRET_OR_PRIVATE_DATA",
            issue_categories=issue_categories + ["secret_or_private_data"],
            severity="critical",
            affected_verticals=[packet.vertical],
            affected_receipts=packet.affected_artifact_refs,
            reason="feedback appears to include secret/private-data risk or declares private data",
            next_actions=next_actions + ["replace feedback with a redacted local summary"],
        )
    if _text_has(CERTIFICATION_PATTERNS, text):
        return PilotFeedbackClassification(
            classification_id=f"classification-{packet.feedback_id}",
            feedback_id=packet.feedback_id,
            classification="BLOCK_CERTIFICATION_CLAIM",
            issue_categories=issue_categories + ["certification_or_proof_request"],
            severity="high",
            affected_verticals=[packet.vertical],
            affected_receipts=packet.affected_artifact_refs,
            should_update_claim_boundary=True,
            reason="feedback asks for a certification/proof/readiness claim outside the pilot scope",
            next_actions=next_actions + ["rewrite requested language as local/offline receipt wording"],
        )
    if packet.consent_status in {"unknown", "insufficient"}:
        return PilotFeedbackClassification(
            classification_id=f"classification-{packet.feedback_id}",
            feedback_id=packet.feedback_id,
            classification="HOLD_OWNER_CONFIRMATION",
            issue_categories=issue_categories + ["consent_gap"],
            severity="medium",
            affected_verticals=[packet.vertical],
            affected_receipts=packet.affected_artifact_refs,
            reason="owner consent is not sufficient for a second local pass",
            next_actions=next_actions + ["request owner-consent clarification"],
        )
    if redaction["decision"] == "HOLD_REVIEW_RECOMMENDED":
        return PilotFeedbackClassification(
            classification_id=f"classification-{packet.feedback_id}",
            feedback_id=packet.feedback_id,
            classification="HOLD_REDACTION_REVIEW",
            issue_categories=issue_categories + ["redaction_review"],
            severity="medium",
            affected_verticals=[packet.vertical],
            affected_receipts=packet.affected_artifact_refs,
            reason="feedback contains content that should be reviewed before a second local pass",
            next_actions=next_actions + ["redact or summarize personal/private details"],
        )
    if len(packet.feedback_text.strip()) < 16 or packet.feedback_category == "other":
        return PilotFeedbackClassification(
            classification_id=f"classification-{packet.feedback_id}",
            feedback_id=packet.feedback_id,
            classification="HOLD_NEEDS_MORE_CONTEXT",
            issue_categories=issue_categories + ["unclear_feedback"],
            severity="low",
            affected_verticals=[packet.vertical],
            affected_receipts=packet.affected_artifact_refs,
            reason="feedback does not provide enough local context to plan a second pass",
            next_actions=next_actions + ["request a clearer local explanation and affected artifact reference"],
        )

    should_add_fixture = packet.feedback_category in {"add_fixture", "wrong_finding", "wrong_allow_hold_block"}
    should_add_negative_control = packet.feedback_category == "add_negative_control"
    should_request_evidence = packet.feedback_category in {"missing_evidence", "request_second_run"}
    should_run_second_pass = packet.feedback_category == "request_second_run" or should_add_fixture or should_request_evidence
    return PilotFeedbackClassification(
        classification_id=f"classification-{packet.feedback_id}",
        feedback_id=packet.feedback_id,
        classification="ACCEPT_AS_FIXTURE_CANDIDATE",
        issue_categories=issue_categories,
        severity="low",
        affected_verticals=[packet.vertical],
        affected_receipts=packet.affected_artifact_refs,
        should_update_finding=packet.feedback_category in {"wrong_finding", "unclear_explanation", "wrong_allow_hold_block"},
        should_update_claim_boundary=packet.feedback_category in {"missing_claim_boundary", "overclaim_concern"},
        should_add_negative_control=should_add_negative_control,
        should_add_fixture=should_add_fixture,
        should_request_evidence=should_request_evidence,
        should_run_second_pass=should_run_second_pass,
        reason="feedback is local, redacted, consent-bounded, and can inform a future local second pass",
        next_actions=next_actions
        + [
            "convert accepted feedback into a fixture or evidence request",
            "schedule a local second-run receipt only after required artifacts are present",
        ],
    )


def classification_to_jsonable(classification: PilotFeedbackClassification) -> dict[str, Any]:
    return classification.model_dump(mode="json", by_alias=True)


def write_sample_classifications() -> dict[str, Any]:
    packets = sample_feedback_packets()
    classifications = [classification_to_jsonable(classify_feedback(packet)) for packet in packets]
    result = {
        "schema": "ResidualOps_PilotFeedbackClassificationSet/v0.1",
        "generated_at": timestamp(),
        "classification_count": len(classifications),
        "classifications": classifications,
    }
    destination = _repo_root() / OUTPUT_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Classify local/offline pilot feedback.")
    parser.add_argument("--sample", action="store_true")
    return parser


def main() -> None:
    build_parser().parse_args()
    result = write_sample_classifications()
    decisions = [item["classification"] for item in result["classifications"]]
    print(f"pilot_feedback_classifier: classifications={result['classification_count']} decisions={decisions}")


if __name__ == "__main__":
    main()
