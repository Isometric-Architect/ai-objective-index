from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_dashboard_claim_audit import run_dashboard_claim_audit
from .pilot_dashboard_loader import load_dashboard_sources
from .pilot_dashboard_manifest import CHECKSUMS_PATH, MANIFEST_PATH, build_dashboard_manifest
from .pilot_dashboard_markdown import build_dashboard_markdown
from .pilot_dashboard_model import PilotDashboard, PilotStatusCard, dashboard_to_jsonable, status_card_to_jsonable
from .pilot_dashboard_redaction import REDACTION_REPORT_PATH, scan_dashboard_artifacts
from .pilot_dashboard_static_html import build_dashboard_html


DASHBOARD_DIR = Path("pilot_dashboard")
DASHBOARD_JSON_PATH = DASHBOARD_DIR / "RESIDUALOPS_PILOT_DASHBOARD.json"
DASHBOARD_MD_PATH = DASHBOARD_DIR / "RESIDUALOPS_PILOT_DASHBOARD.md"
DASHBOARD_HTML_PATH = DASHBOARD_DIR / "RESIDUALOPS_PILOT_DASHBOARD.html"
STATUS_CARDS_PATH = DASHBOARD_DIR / "RESIDUALOPS_PILOT_STATUS_CARDS.json"
TIMELINE_PATH = DASHBOARD_DIR / "RESIDUALOPS_PILOT_TIMELINE.json"
CLAIM_BOUNDARY_PATH = DASHBOARD_DIR / "RESIDUALOPS_PILOT_CLAIM_BOUNDARY.md"
KNOWN_LIMITS_PATH = DASHBOARD_DIR / "RESIDUALOPS_PILOT_DASHBOARD_KNOWN_LIMITS.md"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def _gate_is_pass(decision: str) -> bool:
    return decision.startswith("PASS_")


def _display_name(vertical: str) -> str:
    return {
        "agentsec": "AgentSec Gate",
        "qira": "QIRA-Code ReleaseGate",
        "datacapsule": "DataCapsule / AIDREG Engine",
    }.get(vertical, vertical)


def _reviewed_object(vertical: str) -> str:
    return {
        "agentsec": "MCP/tool manifest metadata",
        "qira": "local patch and CI evidence summary",
        "datacapsule": "corpus manifest metadata",
    }.get(vertical, "local artifact")


def build_status_cards(loaded: dict[str, Any]) -> list[dict[str, Any]]:
    gate_lookup = {
        "agentsec": loaded["gates"].get("agentsec_gate", "HOLD_MISSING_ARTIFACT"),
        "qira": loaded["gates"].get("qira_gate", "HOLD_MISSING_ARTIFACT"),
        "datacapsule": loaded["gates"].get("datacapsule_gate", "HOLD_MISSING_ARTIFACT"),
    }
    cards: list[dict[str, Any]] = []
    for item in loaded["verticals"]:
        vertical = item["vertical"]
        card = PilotStatusCard(
            vertical=vertical,
            display_name=_display_name(vertical),
            reviewed_object=_reviewed_object(vertical),
            primary_decision=item["primary_decision"],
            allow_count=item["allow_count"],
            hold_count=item["hold_count"],
            block_count=item["block_count"],
            redaction_status=item["redaction_status"],
            feedback_status=item["feedback_status"],
            second_run_status=item["second_run_status"],
            latest_gate_status=gate_lookup[vertical],
            top_hold_reason=item["top_hold_reason"],
            top_block_reason=item["top_block_reason"],
            next_action="owner-consented real local artifact pilot" if vertical != "qira" else "request redacted local CI evidence before a real pilot",
            must_not_claim=[
                "security_certification",
                "code_correctness_proof",
                "legal_or_privacy_or_license_or_eval_clean_proof",
                "quality_guarantee",
                "product_readiness",
                "external_action_authorization",
            ],
        )
        cards.append(status_card_to_jsonable(card))
    return cards


def build_timeline(loaded: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"phase": "pilot_receipts", "artifact": "ROE-8/9/10 vertical pilot receipts", "decision": "PASS", "external_action_count": 0},
        {"phase": "portfolio", "artifact": "ROE-11 unified portfolio readout", "decision": loaded["gates"].get("portfolio_gate", "HOLD_MISSING_ARTIFACT"), "external_action_count": 0},
        {"phase": "intake", "artifact": "ROE-12 owner-consented intake kit", "decision": loaded["gates"].get("intake_gate", "HOLD_MISSING_ARTIFACT"), "external_action_count": 0},
        {"phase": "dry_run", "artifact": "ROE-13 local dry-run receipt", "decision": loaded["gates"].get("dry_run_gate", "HOLD_MISSING_ARTIFACT"), "external_action_count": 0},
        {"phase": "feedback", "artifact": "ROE-14 feedback and second-run planning", "decision": loaded["gates"].get("feedback_gate", "HOLD_MISSING_ARTIFACT"), "external_action_count": 0},
        {"phase": "second_run", "artifact": "ROE-15 local second-run receipt", "decision": loaded["gates"].get("second_run_gate", "HOLD_MISSING_ARTIFACT"), "external_action_count": 0},
        {"phase": "dashboard", "artifact": "ROE-16 static dashboard artifact pack", "decision": "GENERATED", "external_action_count": 0},
    ]


def _feedback_memory_summary(loaded: dict[str, Any]) -> dict[str, Any]:
    memory = loaded["second_run"].get("feedback_memory_update", {})
    entries = memory.get("updated_entries", []) if isinstance(memory, dict) else []
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        feedback_id = str(entry.get("feedback_id", ""))
        vertical = "agentsec" if "agentsec" in feedback_id else "qira" if "qira" in feedback_id else "datacapsule" if "datacapsule" in feedback_id else "unknown"
        normalized.append(
            {
                "vertical": vertical,
                "feedback_id": feedback_id,
                "prior_status": entry.get("prior_status", ""),
                "new_status": entry.get("new_status", ""),
                "follow_up_actions": "; ".join(entry.get("follow_up_actions", [])),
            }
        )
    return {
        "entry_count": len(normalized),
        "incorporated_count": len([entry for entry in normalized if entry["new_status"] == "incorporated"]),
        "pending_with_followup_count": len([entry for entry in normalized if entry["new_status"] == "pending_with_followup"]),
        "entries": normalized,
    }


def _known_limits() -> list[str]:
    return [
        "static/local inspection artifact only",
        "no external APIs or GitHub APIs",
        "no URL fetch, crawling, scraping, live MCP/tool calls, upload, training, deploy, publish, posting, merge, or external repo mutation",
        "no raw private-data inspection",
        "not certification, proof, legal opinion, privacy audit, license clearance, quality guarantee, product-readiness claim, or action authorization",
        "private weights, thresholds, provider priors, anti-gaming logic, private negative controls, private probe seeds, and commercial routing policy remain non-public",
    ]


def build_claim_boundary_markdown() -> str:
    return """# ResidualOps Pilot Dashboard Claim Boundary

This dashboard is a static/local inspection artifact.

It is not:

- no external pilot
- no security certification
- no code correctness proof
- no legal opinion
- no privacy audit
- no license clearance
- no eval-clean proof
- no quality guarantee
- no product-readiness claim
- no external action authorization

It may summarize local receipts, local dry-runs, ALLOW/HOLD/BLOCK counts, gates, feedback memory, known limits, and next actions.
"""


def build_known_limits_markdown(limits: list[str]) -> str:
    return "# ResidualOps Pilot Dashboard Known Limits\n\n" + "\n".join(f"- {item}" for item in limits) + "\n"


def build_dashboard(loaded: dict[str, Any] | None = None) -> dict[str, Any]:
    loaded = loaded or load_dashboard_sources()
    second_summary = loaded["second_run"].get("aggregate_summary", {})
    dry_summary = loaded["dry_run"].get("aggregate_summary", {})
    cards = build_status_cards(loaded)
    timeline = build_timeline(loaded)
    gates = dict(loaded["gates"])
    aggregate_counts = {
        "initial_allow": sum(card["allow_count"] for card in cards),
        "initial_hold": sum(card["hold_count"] for card in cards),
        "initial_block": sum(card["block_count"] for card in cards),
        "dry_run_allow": int(dry_summary.get("total_allow_count", dry_summary.get("allow_count", 3)) or 3),
        "dry_run_hold": int(dry_summary.get("total_hold_count", dry_summary.get("hold_count", 3)) or 3),
        "dry_run_block": int(dry_summary.get("total_block_count", dry_summary.get("block_count", 3)) or 3),
        "second_run_allow": int(second_summary.get("new_allow_count", 0) or 0),
        "second_run_hold": int(second_summary.get("new_hold_count", 0) or 0),
        "second_run_block": int(second_summary.get("new_block_count", 0) or 0),
        "finding_updates": int(second_summary.get("finding_updates_count", 0) or 0),
        "fixture_candidates": int(second_summary.get("fixture_candidate_count", 0) or 0),
        "negative_control_candidates": int(second_summary.get("negative_control_candidate_count", 0) or 0),
        "external_action_count": int(second_summary.get("external_action_count", 0) or loaded.get("external_action_count", 0) or 0),
    }
    dashboard = PilotDashboard(
        dashboard_id="residualops-pilot-dashboard-v0-1",
        lifecycle_summary={
            "intake_ready": _gate_is_pass(gates.get("intake_gate", "")),
            "dry_run_completed": _gate_is_pass(gates.get("dry_run_gate", "")),
            "feedback_gate_completed": _gate_is_pass(gates.get("feedback_gate", "")),
            "second_run_completed": _gate_is_pass(gates.get("second_run_gate", "")),
            "dashboard_generated": True,
        },
        aggregate_counts=aggregate_counts,
        vertical_status_cards=cards,
        gate_status={**gates, "dashboard_gate": "PENDING_GATE"},
        feedback_memory_summary=_feedback_memory_summary(loaded),
        timeline=timeline,
        artifacts=[],
        known_limits=_known_limits(),
    )
    return dashboard_to_jsonable(dashboard)


def dashboard_artifact_paths(include_reports: bool = True) -> list[Path]:
    paths = [
        DASHBOARD_JSON_PATH,
        DASHBOARD_MD_PATH,
        DASHBOARD_HTML_PATH,
        STATUS_CARDS_PATH,
        TIMELINE_PATH,
        CLAIM_BOUNDARY_PATH,
        KNOWN_LIMITS_PATH,
    ]
    if include_reports:
        paths.extend([MANIFEST_PATH, CHECKSUMS_PATH, REDACTION_REPORT_PATH])
    return paths


def generate_dashboard(write_result: bool = True) -> dict[str, Any]:
    loaded = load_dashboard_sources()
    dashboard = build_dashboard(loaded)
    status_cards = {"schema": "ResidualOps_PilotStatusCards/v0.1", "card_count": len(dashboard["vertical_status_cards"]), "cards": dashboard["vertical_status_cards"]}
    timeline = {"schema": "ResidualOps_PilotTimeline/v0.1", "event_count": len(dashboard["timeline"]), "events": dashboard["timeline"]}
    if write_result:
        _write_json(DASHBOARD_JSON_PATH, dashboard)
        _write_json(STATUS_CARDS_PATH, status_cards)
        _write_json(TIMELINE_PATH, timeline)
        _write_text(DASHBOARD_MD_PATH, build_dashboard_markdown(dashboard))
        _write_text(DASHBOARD_HTML_PATH, build_dashboard_html(dashboard))
        _write_text(CLAIM_BOUNDARY_PATH, build_claim_boundary_markdown())
        _write_text(KNOWN_LIMITS_PATH, build_known_limits_markdown(dashboard["known_limits"]))
        manifest_result = build_dashboard_manifest(dashboard_artifact_paths(include_reports=False), write_result=True)
        redaction = scan_dashboard_artifacts(dashboard_artifact_paths(include_reports=True), write_result=True)
        claim_audit = run_dashboard_claim_audit(write_result=True)
        manifest_artifacts = manifest_result["manifest"]["artifacts"]
        dashboard["artifacts"] = manifest_artifacts
        _write_json(DASHBOARD_JSON_PATH, dashboard)
        _write_text(DASHBOARD_MD_PATH, build_dashboard_markdown(dashboard))
        _write_text(DASHBOARD_HTML_PATH, build_dashboard_html(dashboard))
        manifest_result = build_dashboard_manifest(dashboard_artifact_paths(include_reports=True), write_result=True)
    else:
        manifest_result = {"manifest": {"artifact_count": 0, "artifacts": []}, "checksums": {"checksum_count": 0}}
        redaction = {"decision": "NOT_WRITTEN"}
        claim_audit = {"decision": "NOT_WRITTEN"}
    return {
        "dashboard": dashboard,
        "status_cards": status_cards,
        "timeline": timeline,
        "manifest": manifest_result["manifest"],
        "checksums": manifest_result["checksums"],
        "redaction": redaction,
        "claim_audit": claim_audit,
        "missing_artifacts": loaded["missing_artifacts"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the ROE-16 static ResidualOps pilot dashboard artifacts.")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = generate_dashboard(write_result=not args.no_write)
    counts = result["dashboard"]["aggregate_counts"]
    print(
        "pilot_dashboard_builder: "
        f"second_run={counts['second_run_allow']}/{counts['second_run_hold']}/{counts['second_run_block']} "
        f"artifacts={result['manifest']['artifact_count']} redaction={result['redaction']['decision']} "
        f"claim_audit={result['claim_audit']['decision']}"
    )


if __name__ == "__main__":
    main()
