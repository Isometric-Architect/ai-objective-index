from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


ROE21_DELTA_PATH = Path("pilot_dashboard") / "ROE21_DASHBOARD_REFRESH_DELTA.json"
ROE21_STATUS_CARDS_PATH = Path("pilot_dashboard") / "ROE21_FEEDBACK_SECOND_RUN_STATUS_CARDS.json"
ROE21_TIMELINE_PATH = Path("pilot_dashboard") / "ROE21_FEEDBACK_SECOND_RUN_TIMELINE.json"
ROE21_MEMORY_PATH = Path("pilot_dashboard") / "ROE21_FEEDBACK_SECOND_RUN_MEMORY_SUMMARY.json"
ROE21_READOUT_PATH = Path("pilot_dashboard") / "ROE21_DASHBOARD_REFRESH_READOUT.md"
ROE21_REDACTION_PATH = Path("pilot_dashboard") / "ROE21_DASHBOARD_REFRESH_REDACTION_REPORT.json"
ROE21_CLAIM_AUDIT_PATH = Path("pilot_dashboard") / "ROE21_DASHBOARD_REFRESH_CLAIM_AUDIT.json"

DASHBOARD_JSON_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.json"
DASHBOARD_MD_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.md"
DASHBOARD_HTML_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.html"
ROE17_MANIFEST_PATH = Path("external_share_pack") / "RESIDUALOPS_EXTERNAL_SAFE_MANIFEST.json"

REQUIRED_ROE21_ARTIFACTS = [
    ROE21_DELTA_PATH,
    ROE21_STATUS_CARDS_PATH,
    ROE21_TIMELINE_PATH,
    ROE21_MEMORY_PATH,
    ROE21_READOUT_PATH,
    ROE21_REDACTION_PATH,
    ROE21_CLAIM_AUDIT_PATH,
]


def _read_json(path: Path) -> dict[str, Any]:
    full = _repo_root() / path
    if not full.exists():
        return {}
    try:
        payload = json.loads(full.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_text(path: Path) -> str:
    full = _repo_root() / path
    if not full.exists():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")


def load_external_share_refresh_sources(paths: list[Path] | None = None) -> dict[str, Any]:
    required = paths or REQUIRED_ROE21_ARTIFACTS
    missing = [str(path).replace("\\", "/") for path in required if not (_repo_root() / path).exists()]
    missing_roe21 = [item for item in missing if item.startswith("pilot_dashboard/ROE21_")]
    return {
        "dashboard_refresh_delta": _read_json(ROE21_DELTA_PATH),
        "status_cards": _read_json(ROE21_STATUS_CARDS_PATH),
        "timeline": _read_json(ROE21_TIMELINE_PATH),
        "feedback_memory": _read_json(ROE21_MEMORY_PATH),
        "refresh_readout": _read_text(ROE21_READOUT_PATH),
        "refresh_redaction": _read_json(ROE21_REDACTION_PATH),
        "refresh_claim_audit": _read_json(ROE21_CLAIM_AUDIT_PATH),
        "source_dashboard": _read_json(DASHBOARD_JSON_PATH),
        "source_dashboard_markdown": _read_text(DASHBOARD_MD_PATH),
        "source_dashboard_html": _read_text(DASHBOARD_HTML_PATH),
        "previous_share_manifest": _read_json(ROE17_MANIFEST_PATH),
        "missing_artifacts": missing,
        "missing_roe21_artifacts": missing_roe21,
        "decision": "HOLD_MISSING_REFRESHED_DASHBOARD" if missing_roe21 else "PASS_REFRESHED_DASHBOARD_LOADED",
        "network_used": False,
        "external_action_used": False,
    }
