from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .feedback_reply_classifier import classification_to_jsonable, classify_feedback_reply
from .feedback_reply_memory_candidate import build_memory_candidate, memory_candidate_to_jsonable
from .feedback_reply_packet import (
    FeedbackReplyPacket,
    packet_to_jsonable,
    sample_packet_paths,
    sample_reply_paths,
    sample_reply_texts,
)
from .feedback_reply_readout import build_feedback_reply_readout
from .feedback_reply_redaction import REDACTION_REPORT_PATH, redact_reply_text, scan_reply_artifacts
from .feedback_reply_router import route_feedback_reply, route_to_jsonable
from .feedback_reply_second_run_candidate import build_second_run_candidate, second_run_candidate_to_jsonable
from .feedback_reply_triage import build_triage_entry, triage_to_jsonable


REPLY_DIR = Path("feedback_replies")
CLASSIFICATION_SAMPLE_PATH = REPLY_DIR / "FEEDBACK_REPLY_CLASSIFICATION_SAMPLE.json"
ROUTE_SAMPLE_PATH = REPLY_DIR / "FEEDBACK_REPLY_ROUTE_SAMPLE.json"
TRIAGE_SAMPLE_PATH = REPLY_DIR / "FEEDBACK_REPLY_TRIAGE_SAMPLE.json"
MEMORY_CANDIDATE_SAMPLE_PATH = REPLY_DIR / "FEEDBACK_REPLY_MEMORY_CANDIDATE_SAMPLE.json"
SECOND_RUN_CANDIDATE_SAMPLE_PATH = REPLY_DIR / "FEEDBACK_REPLY_SECOND_RUN_CANDIDATE_SAMPLE.json"
READOUT_PATH = REPLY_DIR / "FEEDBACK_REPLY_REVIEWER_READOUT.md"
KNOWN_LIMITS_PATH = REPLY_DIR / "FEEDBACK_REPLY_KNOWN_LIMITS.md"


def _write_text(path: Path, content: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _infer_vertical(text: str, default: str = "unknown") -> str:
    lowered = text.lower()
    if any(term in lowered for term in ["agentsec", "tool", "manifest", "permission", "mcp"]):
        return "agentsec"
    if any(term in lowered for term in ["qira", "patch", "ci", "diff", "code", "release"]):
        return "qira"
    if any(term in lowered for term in ["datacapsule", "dataset", "license", "privacy", "eval", "corpus"]):
        return "datacapsule"
    if any(term in lowered for term in ["portfolio", "dashboard", "readout", "message"]):
        return "portfolio"
    return default


def _infer_requested_action(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ["create issue", "post", "comment", "merge", "deploy", "publish"]):
        return "request_external_action"
    if any(term in lowered for term in ["certify", "product ready", "production ready", "prove"]):
        return "request_certification"
    if "second" in lowered and ("run" in lowered or "pass" in lowered):
        return "request_second_run"
    if "evidence" in lowered:
        return "add_evidence"
    if "route" in lowered:
        return "change_route"
    if "finding" in lowered:
        return "fix_finding"
    if "clar" in lowered:
        return "clarify"
    return "other"


def build_feedback_reply_packet(
    text: str,
    reply_id: str,
    source: str = "sample_fixture",
    source_ref: str = "",
    reviewer_type: str = "unknown",
    related_vertical: str = "unknown",
) -> FeedbackReplyPacket:
    redacted, findings = redact_reply_text(text)
    finding_types = {item["finding_type"] for item in findings}
    requested_action = _infer_requested_action(text)
    vertical = related_vertical if related_vertical != "unknown" else _infer_vertical(text)
    lowered = text.lower()
    return FeedbackReplyPacket(
        reply_id=reply_id,
        source=source,
        source_ref=source_ref,
        reviewer_type=reviewer_type,
        related_vertical=vertical,
        related_artifact_refs=[f"pilot_outreach/{vertical}"] if vertical != "unknown" else [],
        reply_text_redacted=redacted,
        contains_private_data_declared=("private " + "dataset") in lowered or "raw pii" in lowered,
        consent_signal="sample_fixture" if source == "sample_fixture" else "explicit_local_review_allowed" if "local" in lowered and "consent" in lowered else "feedback_only",
        requested_action=requested_action,
        external_action_requested=requested_action == "request_external_action",
        certification_or_readiness_claim_requested=requested_action == "request_certification",
        token_or_secret_detected=bool({"token_or_secret", "private_key", "env_content", "raw_private_dataset_row"} & finding_types),
        private_kernel_detected="private_kernel_value" in finding_types,
    )


def _known_limits() -> str:
    return """# Feedback Reply Known Limits

- Reply intake is local/offline only.
- A reply is not consent to external action.
- The pipeline does not send replies, create GitHub issues, post comments, call APIs, fetch URLs, upload data, train models, merge, deploy, or publish packages.
- A reply cannot certify security, prove code correctness, provide legal/privacy/license/eval-clean proof, guarantee quality, claim product readiness, or authorize external action.
"""


def _process_packets(packets: list[FeedbackReplyPacket]) -> dict[str, Any]:
    packet_payloads = [packet_to_jsonable(packet) for packet in packets]
    classifications = []
    routes = []
    triage_entries = []
    memory_candidates = []
    second_run_candidates = []
    for packet in packets:
        classification = classify_feedback_reply(packet)
        route = route_feedback_reply(packet, classification)
        triage = build_triage_entry(packet, classification, route)
        memory = build_memory_candidate(packet, classification, route)
        second_run = build_second_run_candidate(packet, classification, route)
        classifications.append(classification_to_jsonable(classification))
        routes.append(route_to_jsonable(route))
        triage_entries.append(triage_to_jsonable(triage))
        memory_candidates.append(memory_candidate_to_jsonable(memory))
        second_run_candidates.append(second_run_candidate_to_jsonable(second_run))
    return {
        "packets": packet_payloads,
        "classifications": classifications,
        "routes": routes,
        "triage": triage_entries,
        "memory_candidates": memory_candidates,
        "second_run_candidates": second_run_candidates,
    }


def package_feedback_replies(sample: bool = True, input_path: str | None = None) -> dict[str, Any]:
    packets: list[FeedbackReplyPacket] = []
    if input_path:
        path = Path(input_path)
        text = path.read_text(encoding="utf-8")
        packets.append(
            build_feedback_reply_packet(
                text=text,
                reply_id="feedback-reply-local-input-v0-1",
                source="local_file",
                source_ref=str(path),
                reviewer_type="unknown",
            )
        )
    else:
        for vertical, text in sample_reply_texts().items():
            sample_path = sample_reply_paths()[vertical]
            _write_text(sample_path, text + "\n")
            packets.append(
                build_feedback_reply_packet(
                    text=text,
                    reply_id=f"feedback-reply-sample-{vertical}-v0-1",
                    source="sample_fixture",
                    source_ref=str(sample_path).replace("\\", "/"),
                    reviewer_type="security_reviewer" if vertical == "agentsec" else "developer" if vertical == "qira" else "data_steward" if vertical == "datacapsule" else "founder_operator",
                    related_vertical=vertical,
                )
            )
    packet_paths = sample_packet_paths()
    for packet in packets:
        if packet.related_vertical in packet_paths:
            _write_json(packet_paths[packet.related_vertical], packet_to_jsonable(packet))

    bundle = _process_packets(packets)
    classification_payload = {
        "schema": "ResidualOps_FeedbackReplyClassificationSet/v0.1",
        "classification_count": len(bundle["classifications"]),
        "classifications": bundle["classifications"],
    }
    route_payload = {
        "schema": "ResidualOps_FeedbackReplyRouteSet/v0.1",
        "route_count": len(bundle["routes"]),
        "routes": bundle["routes"],
    }
    triage_payload = {
        "schema": "ResidualOps_FeedbackReplyTriageSet/v0.1",
        "triage_count": len(bundle["triage"]),
        "triage": bundle["triage"],
    }
    memory_payload = {
        "schema": "ResidualOps_FeedbackReplyMemoryCandidateSet/v0.1",
        "candidate_count": len(bundle["memory_candidates"]),
        "candidates": bundle["memory_candidates"],
    }
    second_run_payload = {
        "schema": "ResidualOps_FeedbackReplySecondRunCandidateSet/v0.1",
        "candidate_count": len(bundle["second_run_candidates"]),
        "candidates": bundle["second_run_candidates"],
        "second_run_executed": False,
    }
    _write_json(CLASSIFICATION_SAMPLE_PATH, classification_payload)
    _write_json(ROUTE_SAMPLE_PATH, route_payload)
    _write_json(TRIAGE_SAMPLE_PATH, triage_payload)
    _write_json(MEMORY_CANDIDATE_SAMPLE_PATH, memory_payload)
    _write_json(SECOND_RUN_CANDIDATE_SAMPLE_PATH, second_run_payload)
    _write_text(KNOWN_LIMITS_PATH, _known_limits())

    artifact_paths = [
        *sample_reply_paths().values(),
        *sample_packet_paths().values(),
        CLASSIFICATION_SAMPLE_PATH,
        ROUTE_SAMPLE_PATH,
        TRIAGE_SAMPLE_PATH,
        MEMORY_CANDIDATE_SAMPLE_PATH,
        SECOND_RUN_CANDIDATE_SAMPLE_PATH,
        KNOWN_LIMITS_PATH,
    ]
    redaction = scan_reply_artifacts(artifact_paths, write_result=True)
    bundle["redaction"] = redaction
    _write_text(READOUT_PATH, build_feedback_reply_readout(bundle))
    artifact_paths += [READOUT_PATH, REDACTION_REPORT_PATH]
    return {
        **bundle,
        "artifact_paths": [str(path).replace("\\", "/") for path in artifact_paths],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package local/offline feedback replies into reply packets.")
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--input", help="Optional local reply text/Markdown file.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = package_feedback_replies(sample=args.sample or not args.input, input_path=args.input)
    print(
        "feedback_reply_intake: "
        f"packets={len(result['packets'])} classifications={len(result['classifications'])} "
        f"routes={len(result['routes'])} redaction={result['redaction']['decision']} "
        f"second_run_candidates={len(result['second_run_candidates'])}"
    )


if __name__ == "__main__":
    main()
