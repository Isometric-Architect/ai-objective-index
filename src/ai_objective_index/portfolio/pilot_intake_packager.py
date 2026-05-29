from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_consent_record import build_consent_record, consent_record_to_jsonable
from .pilot_intake_feedback_memory import build_feedback_memory_entry, feedback_memory_to_jsonable
from .pilot_intake_packet import (
    AllowedReviewScope,
    IntakeOwnerConsent,
    PilotIntakePacket,
    ProvidedArtifact,
    intake_packet_to_jsonable,
)
from .pilot_intake_redaction import OUTPUT_PATH as REDACTION_PATH
from .pilot_intake_redaction import scan_intake_artifacts
from .pilot_run_plan import build_run_plan, run_plan_to_jsonable
from .pilot_vertical_router import route_intake_packet, route_to_jsonable


OUTPUT_DIR = Path("pilot_intake")
AGENTSEC_PACKET_PATH = OUTPUT_DIR / "PILOT_INTAKE_PACKET_SAMPLE_AGENTSEC.json"
QIRA_PACKET_PATH = OUTPUT_DIR / "PILOT_INTAKE_PACKET_SAMPLE_QIRA.json"
DATACAPSULE_PACKET_PATH = OUTPUT_DIR / "PILOT_INTAKE_PACKET_SAMPLE_DATACAPSULE.json"
CONSENT_TEMPLATE_PATH = OUTPUT_DIR / "PILOT_CONSENT_RECORD_TEMPLATE.md"
INTAKE_FORM_TEMPLATE_PATH = OUTPUT_DIR / "PILOT_INTAKE_FORM_TEMPLATE.md"
RUN_PLAN_PATH = OUTPUT_DIR / "PILOT_RUN_PLAN_SAMPLE.json"
REVIEWER_INSTRUCTIONS_PATH = OUTPUT_DIR / "PILOT_INTAKE_REVIEWER_INSTRUCTIONS.md"
KNOWN_LIMITS_PATH = OUTPUT_DIR / "PILOT_INTAKE_KNOWN_LIMITS.md"
AGENTSEC_ROUTE_PATH = OUTPUT_DIR / "PILOT_VERTICAL_ROUTE_SAMPLE_AGENTSEC.json"
QIRA_ROUTE_PATH = OUTPUT_DIR / "PILOT_VERTICAL_ROUTE_SAMPLE_QIRA.json"
DATACAPSULE_ROUTE_PATH = OUTPUT_DIR / "PILOT_VERTICAL_ROUTE_SAMPLE_DATACAPSULE.json"
CONSENT_RECORD_SAMPLE_PATH = OUTPUT_DIR / "PILOT_CONSENT_RECORD_SAMPLE.json"
FEEDBACK_MEMORY_SAMPLE_PATH = OUTPUT_DIR / "PILOT_INTAKE_FEEDBACK_MEMORY_SAMPLE.json"


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
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _sample_packet(vertical: str) -> PilotIntakePacket:
    if vertical == "agentsec":
        artifact = ProvidedArtifact(
            artifact_type="mcp_manifest",
            local_path="pilot_intake/samples/agentsec_mcp_manifest.json",
            raw_content_included=False,
            contains_private_data_declared=False,
        )
        scope = AllowedReviewScope(local_static_review=True, manifest_only=True)
        label = "AgentSec sample MCP manifest intake"
    elif vertical == "qira":
        artifact = ProvidedArtifact(
            artifact_type="pr_diff",
            local_path="pilot_intake/samples/qira_patch.diff",
            raw_content_included=False,
            contains_private_data_declared=False,
        )
        scope = AllowedReviewScope(local_static_review=True, diff_only=True)
        label = "QIRA sample patch intake"
    else:
        artifact = ProvidedArtifact(
            artifact_type="corpus_manifest",
            local_path="pilot_intake/samples/datacapsule_corpus_manifest.json",
            raw_content_included=False,
            contains_private_data_declared=False,
        )
        scope = AllowedReviewScope(local_static_review=True, manifest_only=True)
        label = "DataCapsule sample corpus manifest intake"
    raw = {"vertical": vertical, "artifact": artifact.model_dump(mode="json")}
    artifact.hash = _stable_hash(raw)
    return PilotIntakePacket(
        intake_id=f"pilot-intake-sample-{vertical}-{artifact.hash}",
        pilot_label=label,
        requested_vertical=vertical,  # type: ignore[arg-type]
        owner_consent=IntakeOwnerConsent(
            status="sample_fixture",
            consent_text="sample fixture only; no external owner file is represented",
            consent_scope="local/static sample intake planning only",
            contact_redacted=True,
        ),
        provided_artifact=artifact,
        allowed_review_scope=scope,
    )


def build_input_packet(input_path: Path, vertical: str = "auto_route") -> PilotIntakePacket:
    artifact_type = "unknown"
    suffix = input_path.suffix.lower()
    if suffix in {".json", ".yaml", ".yml"}:
        artifact_type = "mixed"
    elif suffix in {".diff", ".patch"}:
        artifact_type = "pr_diff"
    return PilotIntakePacket(
        intake_id=f"pilot-intake-local-{_stable_hash(str(input_path))}",
        pilot_label=f"Local intake path: {input_path.name}",
        requested_vertical=vertical if vertical in {"agentsec", "qira", "datacapsule", "auto_route"} else "auto_route",  # type: ignore[arg-type]
        owner_consent=IntakeOwnerConsent(
            status="unknown",
            consent_text="local path supplied without a stored owner consent record",
            consent_scope="not ready until consent is confirmed",
            contact_redacted=True,
        ),
        provided_artifact=ProvidedArtifact(
            artifact_type=artifact_type,  # type: ignore[arg-type]
            local_path=str(input_path),
            raw_content_included=False,
            contains_private_data_declared=None,
        ),
    )


def build_consent_template() -> str:
    return """# Pilot Consent Record Template

Use this template before any owner-consented local pilot.

- Owner or maintainer:
- Artifact label:
- Allowed local review mode:
- Allowed vertical: AgentSec / QIRA / DataCapsule / auto-route
- Retention preference: keep local artifact / keep redacted receipt only / delete after review
- Share preference: private only / redacted summary allowed / public anonymized allowed

Consent boundaries:

- Consent allows local review of explicitly provided artifacts only.
- Consent does not allow cloning, URL fetching, GitHub API calls, PRs, issues, comments, merges, deploys, uploads, model training, live MCP/tool calls, or external tool execution.
- Consent does not create security certification, code correctness proof, legal opinion, privacy audit, license clearance, evaluation-cleanliness proof, quality guarantee, product-readiness claim, or external action authorization.
"""


def build_intake_form_template() -> str:
    return """# Pilot Intake Form Template

## Artifact

- Requested vertical:
- Artifact type:
- Local path or pasted-text ID:
- Raw content included: yes/no
- Private data declared: yes/no/unknown

## Consent

- Consent status: self-owned / owner-provided / sample fixture / unknown
- Consent scope:
- Contact information redacted: yes/no

## Safety Boundary

- No credentials.
- No `.env` content.
- No raw secrets.
- No private kernel values.
- No external actions requested.
"""


def build_reviewer_instructions() -> str:
    return """# Pilot Intake Reviewer Instructions

1. Confirm owner consent and review scope.
2. Confirm the artifact is local and explicitly provided.
3. Run redaction preflight before any pilot receipt packaging.
4. Route the artifact to AgentSec, QIRA, or DataCapsule using artifact type.
5. Run only the local/offline pilot packager for the selected vertical.
6. Produce a claim-bounded receipt and feedback memory entry.

Do not clone repositories, fetch URLs, call GitHub APIs, post comments, create PRs or issues, merge, deploy, upload data, train models, run live MCP/tool calls, execute external tools, use credentials, or claim certification/proof/quality/product readiness/action authorization.
"""


def build_known_limits() -> str:
    return """# Pilot Intake Known Limits

- Intake packets are local/offline planning artifacts.
- Owner consent permits only the local review mode stated in the packet.
- Raw private data should be replaced with a redacted manifest or summary before pilot packaging.
- The kit does not run live pilots by itself.
- The kit does not call external APIs, GitHub APIs, URLs, live MCP servers, or external tools.
- The kit does not certify security, prove code correctness, provide legal/privacy/license/evaluation-cleanliness proof, guarantee quality, claim product readiness, or authorize actions.
"""


def package_pilot_intake(sample: bool = True, vertical: str = "sample", input_path: Path | None = None) -> dict[str, Any]:
    if input_path is not None:
        packets = [build_input_packet(input_path, vertical=vertical)]
    else:
        selected = ["agentsec", "qira", "datacapsule"] if sample or vertical == "sample" else [vertical]
        packets = [_sample_packet(item) for item in selected if item in {"agentsec", "qira", "datacapsule"}]

    packet_paths = {
        "agentsec": AGENTSEC_PACKET_PATH,
        "qira": QIRA_PACKET_PATH,
        "datacapsule": DATACAPSULE_PACKET_PATH,
    }
    route_paths = {
        "agentsec": AGENTSEC_ROUTE_PATH,
        "qira": QIRA_ROUTE_PATH,
        "datacapsule": DATACAPSULE_ROUTE_PATH,
    }

    packet_payloads: list[dict[str, Any]] = []
    route_payloads: list[dict[str, Any]] = []
    for packet in packets:
        packet_payload = intake_packet_to_jsonable(packet)
        route = route_intake_packet(packet)
        route_payload = route_to_jsonable(route)
        packet_payloads.append(packet_payload)
        route_payloads.append(route_payload)
        vertical_id = route.selected_vertical if route.selected_vertical in packet_paths else str(packet.requested_vertical)
        if vertical_id in packet_paths:
            _write_json(packet_paths[vertical_id], packet_payload)
            _write_json(route_paths[vertical_id], route_payload)

    consent_record = build_consent_record(
        intake_id=packets[0].intake_id if packets else "pilot-intake-sample",
        consent_id="pilot-consent-sample-v0-1",
        consent_status="sample_fixture",
        allowed_artifacts=["mcp_manifest", "tool_manifest", "pr_diff", "patch_text", "ci_summary", "dataset_manifest", "corpus_manifest", "dataset_card"],
    )
    sample_route = route_intake_packet(packets[0]) if packets else None
    redaction = scan_intake_artifacts(
        [
            AGENTSEC_PACKET_PATH,
            QIRA_PACKET_PATH,
            DATACAPSULE_PACKET_PATH,
            AGENTSEC_ROUTE_PATH,
            QIRA_ROUTE_PATH,
            DATACAPSULE_ROUTE_PATH,
            CONSENT_RECORD_SAMPLE_PATH,
        ],
        write_result=True,
    )
    run_plan = build_run_plan(sample_route, consent_status=consent_record.consent_status, redaction_decision=redaction["decision"]) if sample_route else None
    feedback = build_feedback_memory_entry(route_payloads[0] if route_payloads else {})

    _write_json(CONSENT_RECORD_SAMPLE_PATH, consent_record_to_jsonable(consent_record))
    if run_plan is not None:
        _write_json(RUN_PLAN_PATH, run_plan_to_jsonable(run_plan))
    _write_json(FEEDBACK_MEMORY_SAMPLE_PATH, feedback_memory_to_jsonable(feedback))
    _write_text(CONSENT_TEMPLATE_PATH, build_consent_template())
    _write_text(INTAKE_FORM_TEMPLATE_PATH, build_intake_form_template())
    _write_text(REVIEWER_INSTRUCTIONS_PATH, build_reviewer_instructions())
    _write_text(KNOWN_LIMITS_PATH, build_known_limits())
    redaction = scan_intake_artifacts(
        [
            AGENTSEC_PACKET_PATH,
            QIRA_PACKET_PATH,
            DATACAPSULE_PACKET_PATH,
            AGENTSEC_ROUTE_PATH,
            QIRA_ROUTE_PATH,
            DATACAPSULE_ROUTE_PATH,
            CONSENT_RECORD_SAMPLE_PATH,
            RUN_PLAN_PATH,
            FEEDBACK_MEMORY_SAMPLE_PATH,
            CONSENT_TEMPLATE_PATH,
            INTAKE_FORM_TEMPLATE_PATH,
            REVIEWER_INSTRUCTIONS_PATH,
            KNOWN_LIMITS_PATH,
        ],
        write_result=True,
    )

    return {
        "packets": packet_payloads,
        "routes": route_payloads,
        "consent_record": consent_record_to_jsonable(consent_record),
        "run_plan": run_plan_to_jsonable(run_plan) if run_plan else {},
        "feedback_memory": feedback_memory_to_jsonable(feedback),
        "redaction": redaction,
        "artifact_paths": [
            str(path).replace("\\", "/")
            for path in [
                AGENTSEC_PACKET_PATH,
                QIRA_PACKET_PATH,
                DATACAPSULE_PACKET_PATH,
                AGENTSEC_ROUTE_PATH,
                QIRA_ROUTE_PATH,
                DATACAPSULE_ROUTE_PATH,
                CONSENT_RECORD_SAMPLE_PATH,
                RUN_PLAN_PATH,
                FEEDBACK_MEMORY_SAMPLE_PATH,
                REDACTION_PATH,
                CONSENT_TEMPLATE_PATH,
                INTAKE_FORM_TEMPLATE_PATH,
                REVIEWER_INSTRUCTIONS_PATH,
                KNOWN_LIMITS_PATH,
            ]
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package local/offline owner-consented pilot intake artifacts.")
    parser.add_argument("--sample", action="store_true", help="Generate all three safe sample intake packets.")
    parser.add_argument("--vertical", choices=["agentsec", "qira", "datacapsule", "sample"], default="sample")
    parser.add_argument("--input", type=Path, default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = package_pilot_intake(sample=args.sample or args.vertical == "sample", vertical=args.vertical, input_path=args.input)
    routes = {route["selected_vertical"]: route["can_generate_pilot_receipt"] for route in result["routes"]}
    print(
        "pilot_intake_packager: "
        f"packets={len(result['packets'])} redaction={result['redaction']['decision']} routes={routes}"
    )


if __name__ == "__main__":
    main()
