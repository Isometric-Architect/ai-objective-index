from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_discovery_personas import OUTREACH_DIR, build_discovery_personas, timestamp, write_personas
from .pilot_feedback_intake_form import FEEDBACK_FORM_PATH, write_feedback_intake_form
from .pilot_feedback_triage import TRIAGE_TAXONOMY_PATH, write_feedback_triage_taxonomy
from .pilot_link_pack import LINK_PACK_PATH, write_link_pack
from .pilot_outreach_claim_guard import CLAIM_AUDIT_PATH, REDACTION_REPORT_PATH, run_outreach_claim_audit, run_outreach_redaction
from .pilot_outreach_operator_checklist import (
    CLAIM_BOUNDARY_PATH,
    DO_NOT_SEND_GUARD_PATH,
    FAQ_PATH,
    KNOWN_LIMITS_PATH,
    OPERATOR_CHECKLIST_PATH,
    write_operator_artifacts,
)


DRAFTS_INDEX_PATH = OUTREACH_DIR / "PILOT_OUTREACH_DRAFTS.json"

DRAFT_PATHS = {
    "general": OUTREACH_DIR / "PILOT_FEEDBACK_REQUEST_DRAFT_GENERAL.md",
    "agentsec": OUTREACH_DIR / "PILOT_FEEDBACK_REQUEST_DRAFT_AGENTSEC.md",
    "qira": OUTREACH_DIR / "PILOT_FEEDBACK_REQUEST_DRAFT_QIRA.md",
    "datacapsule": OUTREACH_DIR / "PILOT_FEEDBACK_REQUEST_DRAFT_DATACAPSULE.md",
    "technical_reviewer": OUTREACH_DIR / "PILOT_FEEDBACK_REQUEST_DRAFT_TECHNICAL_REVIEWER.md",
    "founder_or_operator": OUTREACH_DIR / "PILOT_FEEDBACK_REQUEST_DRAFT_FOUNDER_OR_OPERATOR.md",
}


def _claim_boundary() -> dict[str, bool]:
    return {
        "not_security_certification": True,
        "not_code_correctness_proof": True,
        "not_legal_opinion": True,
        "not_privacy_audit": True,
        "not_license_clearance": True,
        "not_eval_clean_proof": True,
        "not_quality_guarantee": True,
        "not_product_ready": True,
        "no_external_action_authorization": True,
        "manual_only": True,
    }


def _body(vertical_label: str, focus: str, ask: str) -> str:
    return f"""Hi,

I'm looking for feedback on a static local demo/share pack for ResidualOps, especially the {vertical_label} part.

What it shows:
- {focus}
- local/offline receipt artifacts;
- ALLOW/HOLD/BLOCK findings;
- known limits and claim boundaries.

What it is not:
- not a product-ready system;
- not security certification;
- not code correctness proof;
- not legal, privacy, license, or eval-clean proof;
- not a quality guarantee;
- no external action automation.

What I would value:
- {ask}
- unclear claims;
- bad UX in the dashboard or operator script;
- missing evidence;
- wrong HOLD/BLOCK wording.

Please do not send tokens, credentials, raw PII, private datasets, private keys, or private kernel details. If you want to provide an artifact for a future pilot, the next step should be a separate owner-consented local/offline intake.
"""


def build_outreach_drafts() -> list[dict[str, Any]]:
    specs = [
        ("general", "manual_email", "portfolio", "three ResidualOps verticals and the external-safe dashboard", "tell me whether the workflow is understandable and where the claims feel too strong"),
        ("agentsec", "manual_dm", "agentsec", "AgentSec manifest review receipts and tool/MCP permission-scope boundaries", "point out missing manifest checks or unclear HOLD/BLOCK reasons"),
        ("qira", "manual_github_issue", "qira", "QIRA task packet, behavior contract, and release-gate receipt shape", "tell me what CI or reviewer evidence should remain required"),
        ("datacapsule", "manual_discussion", "datacapsule", "DataCapsule corpus-manifest review and use-boundary output", "flag missing source, rights, privacy, or eval-overlap fields"),
        ("technical_reviewer", "manual_email", "technical_reviewer", "packet -> check/probe -> receipt -> feedback memory architecture", "stress-test the architecture and find unclear boundaries"),
        ("founder_or_operator", "internal_note", "founder_or_operator", "bounded customer-discovery walkthrough and operator script", "tell me what would help a founder/operator understand the value without overclaiming"),
    ]
    drafts: list[dict[str, Any]] = []
    for draft_id, channel, persona, focus, ask in specs:
        drafts.append(
            {
                "schema": "ResidualOps_PilotOutreachDraft/v0.1",
                "draft_id": draft_id,
                "target_persona": persona,
                "channel": channel,
                "title": f"Feedback request: ResidualOps {persona.replace('_', ' ')} review",
                "body": _body(persona, focus, ask),
                "links_to_include": [
                    "pilot_outreach/PILOT_LINK_PACK.md",
                    "external_share_pack/README_EXTERNAL_SAFE_DEMO.md",
                    "external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_DEMO.html",
                ],
                "ask": ask,
                "claim_boundary": _claim_boundary(),
                "must_not_claim": [
                    "revolutionary",
                    "guaranteed",
                    "certified",
                    "production-ready",
                    "secure",
                    "safe",
                    "proven",
                    "official standard",
                    "everyone should use it",
                ],
                "manual_post_required": True,
                "auto_send_performed": False,
                "external_api_used": False,
            }
        )
    return drafts


def _write_text(path: Path, content: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_outreach_drafts() -> dict[str, Any]:
    drafts = build_outreach_drafts()
    for draft in drafts:
        path = DRAFT_PATHS[draft["draft_id"]]
        content = f"# {draft['title']}\n\nChannel: `{draft['channel']}`\n\n{draft['body'].rstrip()}\n"
        _write_text(path, content)
    payload = {
        "schema": "ResidualOps_PilotOutreachDraftIndex/v0.1",
        "generated_at": timestamp(),
        "draft_count": len(drafts),
        "drafts": drafts,
        "manual_only": True,
        "auto_send_performed": False,
        "external_api_used": False,
    }
    _write_json(DRAFTS_INDEX_PATH, payload)
    return payload


def outreach_artifact_paths(include_reports: bool = True) -> list[Path]:
    paths = [
        DRAFTS_INDEX_PATH,
        *DRAFT_PATHS.values(),
        FEEDBACK_FORM_PATH,
        TRIAGE_TAXONOMY_PATH,
        LINK_PACK_PATH,
        FAQ_PATH,
        CLAIM_BOUNDARY_PATH,
        OPERATOR_CHECKLIST_PATH,
        DO_NOT_SEND_GUARD_PATH,
        KNOWN_LIMITS_PATH,
        OUTREACH_DIR / "PILOT_DISCOVERY_PERSONAS.json",
        OUTREACH_DIR / "PILOT_LINK_PACK.json",
    ]
    if include_reports:
        paths.extend([REDACTION_REPORT_PATH, CLAIM_AUDIT_PATH])
    return paths


def generate_outreach_pack(write_result: bool = True) -> dict[str, Any]:
    if write_result:
        personas = write_personas()
        drafts = write_outreach_drafts()
        form = write_feedback_intake_form()
        triage = write_feedback_triage_taxonomy()
        links = write_link_pack()
        write_operator_artifacts()
        redaction = run_outreach_redaction(outreach_artifact_paths(include_reports=False), write_result=True)
        claim_audit = run_outreach_claim_audit(outreach_artifact_paths(include_reports=False), write_result=True)
    else:
        personas = {"persona_count": len(build_discovery_personas())}
        drafts = {"draft_count": len(build_outreach_drafts())}
        form = ""
        triage = {"category_count": 0}
        links = {}
        redaction = {"decision": "NOT_WRITTEN"}
        claim_audit = {"decision": "NOT_WRITTEN"}
    return {
        "personas": personas,
        "drafts": drafts,
        "feedback_form_length": len(form),
        "triage": triage,
        "links": links,
        "redaction": redaction,
        "claim_audit": claim_audit,
        "auto_send_performed": False,
        "external_api_used": False,
        "external_actions_performed": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate ROE-18 manual-only pilot outreach drafts.")
    parser.add_argument("--generate", action="store_true", help="Generate the outreach draft pack.")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = generate_outreach_pack(write_result=not args.no_write)
    print(
        "pilot_outreach_drafts: "
        f"personas={result['personas'].get('persona_count', 0)} "
        f"drafts={result['drafts'].get('draft_count', 0)} "
        f"redaction={result['redaction'].get('decision', 'UNKNOWN')} "
        f"claim_audit={result['claim_audit'].get('decision', 'UNKNOWN')} "
        "auto_send=False external_api=False"
    )


if __name__ == "__main__":
    main()
