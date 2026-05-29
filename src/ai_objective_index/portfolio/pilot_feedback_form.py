from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_feedback_classifier import classify_feedback, classification_to_jsonable
from .pilot_feedback_memory_update import build_feedback_memory_update, memory_update_to_jsonable
from .pilot_feedback_packet import feedback_packet_to_jsonable, sample_feedback_packets
from .pilot_feedback_redaction import REDACTION_REPORT_PATH, scan_feedback_artifacts
from .pilot_second_run_gate import evaluate_second_run_gate, second_run_gate_to_jsonable
from .pilot_second_run_plan import build_second_run_plan, second_run_plan_to_jsonable
from .pilot_second_run_readout import build_second_run_readout


FEEDBACK_DIR = Path("pilot_feedback")
FORM_TEMPLATE_PATH = FEEDBACK_DIR / "PILOT_FEEDBACK_FORM_TEMPLATE.md"
AGENTSEC_PACKET_PATH = FEEDBACK_DIR / "PILOT_FEEDBACK_PACKET_SAMPLE_AGENTSEC.json"
QIRA_PACKET_PATH = FEEDBACK_DIR / "PILOT_FEEDBACK_PACKET_SAMPLE_QIRA.json"
DATACAPSULE_PACKET_PATH = FEEDBACK_DIR / "PILOT_FEEDBACK_PACKET_SAMPLE_DATACAPSULE.json"
CLASSIFICATION_SAMPLE_PATH = FEEDBACK_DIR / "PILOT_FEEDBACK_CLASSIFICATION_SAMPLE.json"
SECOND_RUN_PLAN_SAMPLE_PATH = FEEDBACK_DIR / "PILOT_SECOND_RUN_PLAN_SAMPLE.json"
MEMORY_UPDATE_SAMPLE_PATH = FEEDBACK_DIR / "PILOT_FEEDBACK_MEMORY_UPDATE_SAMPLE.json"
REVIEWER_READOUT_PATH = FEEDBACK_DIR / "PILOT_SECOND_RUN_REVIEWER_READOUT.md"
KNOWN_LIMITS_PATH = FEEDBACK_DIR / "PILOT_FEEDBACK_KNOWN_LIMITS.md"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_feedback_form_template() -> str:
    return """# Pilot Feedback Form Template

Use this form for local/offline feedback on a ResidualOps pilot readout.

## Review Target

- Pilot or dry-run ID:
- Vertical: AgentSec / QIRA / DataCapsule / portfolio
- Reviewed artifact path:

## Reviewer and Consent

- Reviewer type: owner / maintainer / internal / external / data steward
- Consent status: self-owned / owner-provided / sample fixture / insufficient / unknown
- Do you consent to local/offline review of the provided feedback artifact?

## Feedback

- What finding seemed wrong or unclear?
- What local evidence do you have?
- What change are you requesting?
- Do you request a second local pass?

## Redaction Boundary

Do not include tokens, passwords, private keys, `.env` contents, raw PII, private datasets, credentials, private kernel values, provider priors, weights, thresholds, private negative-control seeds, private probe seeds, or commercial routing policy.

## Claim Boundary

This feedback form is not certification, legal/privacy/license/eval-clean proof, code correctness proof, product readiness, quality guarantee, or external action authorization.
"""


def build_known_limits() -> str:
    return """# Pilot Feedback Known Limits

- Feedback is local/offline only.
- Feedback can request clarification, fixture candidates, evidence requests, claim-boundary updates, or a future local second pass.
- Feedback does not authorize GitHub API calls, issue/PR/comment creation, cloning, URL fetching, live MCP/tool calls, external tool execution, merge, deploy, package publish, upload, or model training.
- Feedback does not certify security, prove correctness, provide legal/privacy/license/evaluation proof, guarantee quality, claim product readiness, or authorize external actions.
- The second-run plan does not execute by default.
"""


def package_pilot_feedback(sample: bool = True) -> dict[str, Any]:
    packets = sample_feedback_packets() if sample else sample_feedback_packets()
    packet_payloads = [feedback_packet_to_jsonable(packet) for packet in packets]
    packet_paths = {
        "agentsec": AGENTSEC_PACKET_PATH,
        "qira": QIRA_PACKET_PATH,
        "datacapsule": DATACAPSULE_PACKET_PATH,
    }
    for payload in packet_payloads:
        vertical = payload.get("vertical")
        if vertical in packet_paths:
            _write_json(packet_paths[vertical], payload)

    classifications = []
    plans = []
    gates = []
    memory_updates = []
    for packet in packets:
        classification = classify_feedback(packet)
        plan = build_second_run_plan(packet, classification)
        gate = evaluate_second_run_gate(packet, classification, plan)
        memory_update = build_feedback_memory_update(packet, classification)
        classifications.append(classification_to_jsonable(classification))
        plans.append(second_run_plan_to_jsonable(plan))
        gates.append(second_run_gate_to_jsonable(gate))
        memory_updates.append(memory_update_to_jsonable(memory_update))

    classification_payload = {
        "schema": "ResidualOps_PilotFeedbackClassificationSet/v0.1",
        "classification_count": len(classifications),
        "classifications": classifications,
    }
    plan_payload = {
        "schema": "ResidualOps_PilotSecondRunPlanSet/v0.1",
        "plan_count": len(plans),
        "plans": plans,
        "second_run_executed": False,
    }
    memory_payload = {
        "schema": "ResidualOps_PilotFeedbackMemoryUpdateSet/v0.1",
        "update_count": len(memory_updates),
        "updates": memory_updates,
    }
    bundle = {
        "feedback_packets": packet_payloads,
        "classifications": classifications,
        "second_run_plans": plans,
        "second_run_gates": gates,
        "memory_updates": memory_updates,
    }

    _write_json(CLASSIFICATION_SAMPLE_PATH, classification_payload)
    _write_json(SECOND_RUN_PLAN_SAMPLE_PATH, plan_payload)
    _write_json(MEMORY_UPDATE_SAMPLE_PATH, memory_payload)
    _write_text(FORM_TEMPLATE_PATH, build_feedback_form_template())
    _write_text(REVIEWER_READOUT_PATH, build_second_run_readout(bundle))
    _write_text(KNOWN_LIMITS_PATH, build_known_limits())
    redaction = scan_feedback_artifacts(
        [
            AGENTSEC_PACKET_PATH,
            QIRA_PACKET_PATH,
            DATACAPSULE_PACKET_PATH,
            CLASSIFICATION_SAMPLE_PATH,
            SECOND_RUN_PLAN_SAMPLE_PATH,
            MEMORY_UPDATE_SAMPLE_PATH,
            FORM_TEMPLATE_PATH,
            REVIEWER_READOUT_PATH,
            KNOWN_LIMITS_PATH,
        ],
        write_result=True,
    )
    return {
        **bundle,
        "redaction": redaction,
        "artifact_paths": [
            str(path).replace("\\", "/")
            for path in [
                FORM_TEMPLATE_PATH,
                AGENTSEC_PACKET_PATH,
                QIRA_PACKET_PATH,
                DATACAPSULE_PACKET_PATH,
                CLASSIFICATION_SAMPLE_PATH,
                SECOND_RUN_PLAN_SAMPLE_PATH,
                MEMORY_UPDATE_SAMPLE_PATH,
                REVIEWER_READOUT_PATH,
                REDACTION_REPORT_PATH,
                KNOWN_LIMITS_PATH,
            ]
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package local/offline pilot feedback and second-run planning artifacts.")
    parser.add_argument("--sample", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = package_pilot_feedback(sample=args.sample or True)
    decisions = [item["classification"] for item in result["classifications"]]
    statuses = [item["run_status"] for item in result["second_run_plans"]]
    print(
        "pilot_feedback_form: "
        f"packets={len(result['feedback_packets'])} redaction={result['redaction']['decision']} "
        f"classifications={decisions} plans={statuses}"
    )


if __name__ == "__main__":
    main()
