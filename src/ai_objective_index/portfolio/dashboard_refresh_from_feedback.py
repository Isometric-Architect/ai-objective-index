from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .dashboard_refresh_claim_audit import run_dashboard_refresh_claim_audit
from .dashboard_refresh_delta import build_dashboard_refresh_delta, delta_to_jsonable
from .dashboard_refresh_feedback_memory import build_dashboard_refresh_feedback_memory_summary
from .dashboard_refresh_loader import load_dashboard_refresh_sources
from .dashboard_refresh_readout import build_dashboard_refresh_readout
from .dashboard_refresh_redaction import scan_dashboard_refresh_artifacts
from .dashboard_refresh_status_cards import build_dashboard_refresh_status_cards
from .dashboard_refresh_timeline import build_dashboard_refresh_timeline


DASHBOARD_DIR = Path("pilot_dashboard")
DELTA_PATH = DASHBOARD_DIR / "ROE21_DASHBOARD_REFRESH_DELTA.json"
STATUS_CARDS_PATH = DASHBOARD_DIR / "ROE21_FEEDBACK_SECOND_RUN_STATUS_CARDS.json"
TIMELINE_PATH = DASHBOARD_DIR / "ROE21_FEEDBACK_SECOND_RUN_TIMELINE.json"
MEMORY_SUMMARY_PATH = DASHBOARD_DIR / "ROE21_FEEDBACK_SECOND_RUN_MEMORY_SUMMARY.json"
READOUT_PATH = DASHBOARD_DIR / "ROE21_DASHBOARD_REFRESH_READOUT.md"
STALE_NOTICE_PATH = DASHBOARD_DIR / "ROE21_EXTERNAL_SHARE_PACK_STALE_NOTICE.md"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_external_share_pack_stale_notice() -> str:
    return """# ROE-21 External Share Pack Stale Notice

The ROE-17 external-safe share pack was valid at its creation time.

It is now marked stale because ROE-20 added a feedback-to-second-run bridge result:

- AgentSec has a local feedback second-run result.
- QIRA remains skipped with missing local artifact context.
- DataCapsule remains skipped with missing local artifact context.
- Portfolio remains skipped with missing local artifact context.

Do not use the ROE-17 share pack as the latest external review artifact until it is regenerated from the ROE-21 dashboard refresh.

This stale notice is not a product update, external pilot, certification, proof, legal/privacy/license/eval-clean conclusion, quality guarantee, product-readiness claim, or external action authorization.
"""


def dashboard_refresh_artifact_paths(include_reports: bool = True) -> list[Path]:
    paths = [
        DELTA_PATH,
        STATUS_CARDS_PATH,
        TIMELINE_PATH,
        MEMORY_SUMMARY_PATH,
        READOUT_PATH,
        STALE_NOTICE_PATH,
    ]
    if include_reports:
        paths.extend(
            [
                DASHBOARD_DIR / "ROE21_DASHBOARD_REFRESH_REDACTION_REPORT.json",
                DASHBOARD_DIR / "ROE21_DASHBOARD_REFRESH_CLAIM_AUDIT.json",
            ]
        )
    return paths


def refresh_dashboard_from_feedback(write_result: bool = True) -> dict[str, Any]:
    loaded = load_dashboard_refresh_sources()
    delta = delta_to_jsonable(build_dashboard_refresh_delta(loaded))
    status_cards = build_dashboard_refresh_status_cards(loaded)
    timeline = build_dashboard_refresh_timeline(loaded)
    memory_summary = build_dashboard_refresh_feedback_memory_summary(loaded)
    readout = build_dashboard_refresh_readout(delta, status_cards, memory_summary)
    stale_notice = build_external_share_pack_stale_notice()

    status_payload = {
        "schema": "ResidualOps_DashboardRefreshStatusCards/v0.1",
        "refresh_id": delta["refresh_id"],
        "card_count": len(status_cards),
        "cards": status_cards,
    }
    if write_result:
        _write_json(DELTA_PATH, delta)
        _write_json(STATUS_CARDS_PATH, status_payload)
        _write_json(TIMELINE_PATH, timeline)
        _write_json(MEMORY_SUMMARY_PATH, memory_summary)
        _write_text(READOUT_PATH, readout)
        _write_text(STALE_NOTICE_PATH, stale_notice)
        scan_paths = dashboard_refresh_artifact_paths(include_reports=False)
        redaction = scan_dashboard_refresh_artifacts(scan_paths, write_result=True)
        claim_audit = run_dashboard_refresh_claim_audit(scan_paths, write_result=True)
    else:
        redaction = {"decision": "NOT_WRITTEN", "finding_count": 0}
        claim_audit = {"decision": "NOT_WRITTEN", "risky_phrase_count": 0}

    return {
        "loaded": loaded,
        "delta": delta,
        "status_cards": status_payload,
        "timeline": timeline,
        "memory_summary": memory_summary,
        "readout": readout,
        "stale_notice": stale_notice,
        "redaction": redaction,
        "claim_audit": claim_audit,
        "artifact_paths": [str(path).replace("\\", "/") for path in dashboard_refresh_artifact_paths(include_reports=True)],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh the static dashboard from ROE-20 feedback second-run artifacts.")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = refresh_dashboard_from_feedback(write_result=not args.no_write)
    after = result["delta"]["aggregate_after"]
    print(
        "dashboard_refresh_from_feedback: "
        f"selected={after['feedback_bridge_selected_count']} skipped={after['feedback_bridge_skipped_count']} "
        f"executed={after['feedback_bridge_executed_count']} redaction={result['redaction']['decision']} "
        f"claim_audit={result['claim_audit']['decision']}"
    )


if __name__ == "__main__":
    main()
