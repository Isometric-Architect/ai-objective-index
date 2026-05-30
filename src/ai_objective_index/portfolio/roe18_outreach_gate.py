from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_discovery_personas import PERSONAS_PATH
from .pilot_feedback_intake_form import FEEDBACK_FORM_PATH
from .pilot_feedback_triage import TRIAGE_TAXONOMY_PATH
from .pilot_link_pack import LINK_PACK_PATH
from .pilot_outreach_claim_guard import CLAIM_AUDIT_PATH, REDACTION_REPORT_PATH
from .pilot_outreach_drafts import DRAFTS_INDEX_PATH, DRAFT_PATHS, generate_outreach_pack
from .pilot_outreach_operator_checklist import (
    CLAIM_BOUNDARY_PATH,
    DO_NOT_SEND_GUARD_PATH,
    FAQ_PATH,
    KNOWN_LIMITS_PATH,
    OPERATOR_CHECKLIST_PATH,
)


OUTPUT_DIR = Path("public_launch") / "roe18"
GATE_RESULT_PATH = OUTPUT_DIR / "ROE18_OUTREACH_GATE_RESULT.json"
SUMMARY_PATH = OUTPUT_DIR / "ROE18_OUTREACH_SUMMARY.md"
NEXT_ACTIONS_PATH = OUTPUT_DIR / "ROE18_NEXT_ACTIONS.md"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def _required_artifacts() -> list[Path]:
    return [
        PERSONAS_PATH,
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
        REDACTION_REPORT_PATH,
        CLAIM_AUDIT_PATH,
    ]


def _summary_markdown(result: dict[str, Any]) -> str:
    return f"""# ROE-18 Outreach Summary

Gate decision: `{result['decision']}`

| Field | Value |
| --- | --- |
| Personas | `{result['persona_count']}` |
| Drafts | `{result['draft_count']}` |
| Triage categories | `{result['triage_category_count']}` |
| Redaction | `{result['redaction_decision']}` |
| Claim audit | `{result['claim_audit_decision']}` |
| Auto-send | `{result['auto_send_performed']}` |
| External API used | `{result['external_api_used']}` |

ROE-18 prepares manual-only feedback discovery materials. It performs no outreach and does not authorize product-readiness, certification, proof, quality, or external-action claims.
"""


def _next_actions_markdown(result: dict[str, Any]) -> str:
    next_step = "ROE-19 Feedback Reply Packet Intake" if result["decision"] == "PASS_MANUAL_OUTREACH_DRAFTS_READY" else "resolve ROE-18 HOLD/BLOCK findings"
    return f"""# ROE-18 Next Actions

Decision: `{result['decision']}`

Recommended next package: {next_step}.

Use one draft manually only after reviewing the do-not-send guard and claim boundary. Do not auto-send, post, create issues, call APIs, use tokens, attach raw private data, or promise certification/product readiness.
"""


def run_roe18_gate(write_result: bool = True, ensure_pack: bool = True) -> dict[str, Any]:
    generated = generate_outreach_pack(write_result=True) if ensure_pack else {}
    personas = generated.get("personas") if generated else _read_json(PERSONAS_PATH)
    drafts = generated.get("drafts") if generated else _read_json(DRAFTS_INDEX_PATH)
    triage = generated.get("triage") if generated else _read_json(TRIAGE_TAXONOMY_PATH)
    redaction = generated.get("redaction") if generated else _read_json(REDACTION_REPORT_PATH)
    claim_audit = generated.get("claim_audit") if generated else _read_json(CLAIM_AUDIT_PATH)
    missing = [str(path).replace("\\", "/") for path in _required_artifacts() if not (_repo_root() / path).exists()]
    auto_send = bool(generated.get("auto_send_performed", False) or drafts.get("auto_send_performed", False))
    external_api = bool(generated.get("external_api_used", False) or drafts.get("external_api_used", False))
    private_kernel = bool(redaction.get("private_kernel_exposed", False))
    token_printed = bool(redaction.get("token_printed", False))
    if missing and any("DRAFT" in item or "PERSONAS" in item for item in missing):
        decision = "HOLD_MISSING_DRAFTS"
    elif missing and any("LINK" in item for item in missing):
        decision = "HOLD_MISSING_LINKS"
    elif missing:
        decision = "HOLD_MISSING_DRAFTS"
    elif redaction.get("decision") == "BLOCK_SENSITIVE_CONTENT" or token_printed:
        decision = "BLOCK_SECRET_FINDING"
    elif claim_audit.get("decision") == "BLOCK_OVERCLAIM":
        decision = "BLOCK_OVERCLAIM"
    elif auto_send:
        decision = "BLOCK_AUTO_SEND"
    elif external_api:
        decision = "BLOCK_EXTERNAL_API"
    elif private_kernel:
        decision = "BLOCK_PRIVATE_KERNEL_DISCLOSURE"
    elif redaction.get("decision") != "PASS_REDACTED":
        decision = "HOLD_REDACTION_REVIEW"
    else:
        decision = "PASS_MANUAL_OUTREACH_DRAFTS_READY"
    result = {
        "schema": "ResidualOps_ROE18OutreachGate/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "persona_count": int(personas.get("persona_count", 0) or 0),
        "draft_count": int(drafts.get("draft_count", 0) or 0),
        "triage_category_count": int(triage.get("category_count", 0) or 0),
        "missing_artifacts": missing,
        "redaction_decision": redaction.get("decision", "UNKNOWN"),
        "redaction_findings": int(redaction.get("finding_count", 0) or 0),
        "claim_audit_decision": claim_audit.get("decision", "UNKNOWN"),
        "claim_audit_findings": int(claim_audit.get("risky_phrase_count", 0) or 0),
        "auto_send_performed": auto_send,
        "external_api_used": external_api,
        "external_actions_performed": False,
        "token_printed": token_printed,
        "private_kernel_exposed": private_kernel,
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
    parser = argparse.ArgumentParser(description="Run the ROE-18 manual outreach draft gate.")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-generate", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_roe18_gate(write_result=not args.no_write, ensure_pack=not args.no_generate)
    print(
        "roe18_outreach_gate: "
        f"{result['decision']} personas={result['persona_count']} drafts={result['draft_count']} "
        f"redaction={result['redaction_decision']} claim_audit={result['claim_audit_decision']} "
        f"auto_send={result['auto_send_performed']} external_api={result['external_api_used']}"
    )


if __name__ == "__main__":
    main()
