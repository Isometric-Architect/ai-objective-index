from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


DASHBOARD_JSON_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.json"
DASHBOARD_MD_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.md"
DASHBOARD_HTML_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.html"
DASHBOARD_STATUS_CARDS_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_STATUS_CARDS.json"
DASHBOARD_TIMELINE_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_TIMELINE.json"

ROE20_SELECTION_PATH = Path("feedback_second_runs") / "ROE20_FEEDBACK_SECOND_RUN_SELECTION_REPORT.json"
ROE20_TRACE_PATH = Path("feedback_second_runs") / "ROE20_FEEDBACK_SECOND_RUN_TRACE.json"
ROE20_RECEIPT_PATH = Path("feedback_second_runs") / "ROE20_FEEDBACK_SECOND_RUN_RECEIPT.json"
ROE20_MEMORY_PATH = Path("feedback_second_runs") / "ROE20_FEEDBACK_SECOND_RUN_MEMORY_UPDATE.json"
ROE20_READOUT_PATH = Path("feedback_second_runs") / "ROE20_FEEDBACK_SECOND_RUN_REVIEWER_READOUT.md"


REQUIRED_ROE20_ARTIFACTS = [
    ROE20_SELECTION_PATH,
    ROE20_TRACE_PATH,
    ROE20_RECEIPT_PATH,
    ROE20_MEMORY_PATH,
    ROE20_READOUT_PATH,
]
EXPECTED_DASHBOARD_ARTIFACTS = [
    DASHBOARD_JSON_PATH,
    DASHBOARD_MD_PATH,
    DASHBOARD_HTML_PATH,
    DASHBOARD_STATUS_CARDS_PATH,
    DASHBOARD_TIMELINE_PATH,
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


def load_dashboard_refresh_sources(paths: list[Path] | None = None) -> dict[str, Any]:
    required = paths or [*REQUIRED_ROE20_ARTIFACTS, *EXPECTED_DASHBOARD_ARTIFACTS]
    missing = [str(path).replace("\\", "/") for path in required if not (_repo_root() / path).exists()]
    missing_roe20 = [item for item in missing if item.startswith("feedback_second_runs/")]
    return {
        "source_dashboard": _read_json(DASHBOARD_JSON_PATH),
        "source_dashboard_markdown": _read_text(DASHBOARD_MD_PATH),
        "source_dashboard_html": _read_text(DASHBOARD_HTML_PATH),
        "source_status_cards": _read_json(DASHBOARD_STATUS_CARDS_PATH),
        "source_timeline": _read_json(DASHBOARD_TIMELINE_PATH),
        "selection_report": _read_json(ROE20_SELECTION_PATH),
        "bridge_trace": _read_json(ROE20_TRACE_PATH),
        "bridge_receipt": _read_json(ROE20_RECEIPT_PATH),
        "memory_update": _read_json(ROE20_MEMORY_PATH),
        "bridge_readout": _read_text(ROE20_READOUT_PATH),
        "missing_artifacts": missing,
        "missing_roe20_artifacts": missing_roe20,
        "decision": "HOLD_MISSING_FEEDBACK_SECOND_RUN" if missing_roe20 else "LOADED",
        "network_used": False,
        "external_action_used": False,
    }
