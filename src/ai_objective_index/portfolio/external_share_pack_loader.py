from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


SOURCE_ARTIFACTS = {
    "dashboard_json": Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.json",
    "dashboard_md": Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.md",
    "dashboard_html": Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.html",
    "dashboard_manifest": Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD_MANIFEST.json",
    "claim_boundary": Path("pilot_dashboard") / "RESIDUALOPS_PILOT_CLAIM_BOUNDARY.md",
    "redaction_report": Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD_REDACTION_REPORT.json",
}


def _read_text(path: Path) -> str:
    full = _repo_root() / path
    if not full.exists() or not full.is_file():
        return ""
    return full.read_text(encoding="utf-8", errors="ignore")


def _read_json(path: Path) -> dict[str, Any]:
    text = _read_text(path)
    if not text:
        return {}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_external_share_sources() -> dict[str, Any]:
    artifacts: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for key, path in SOURCE_ARTIFACTS.items():
        exists = (_repo_root() / path).exists()
        if not exists:
            missing.append(str(path).replace("\\", "/"))
        artifacts[key] = {
            "path": str(path).replace("\\", "/"),
            "exists": exists,
            "text": _read_text(path) if path.suffix.lower() in {".md", ".html"} else "",
            "json": _read_json(path) if path.suffix.lower() == ".json" else {},
        }
    return {
        "decision": "HOLD_MISSING_SOURCE_DASHBOARD" if missing else "PASS_SOURCE_DASHBOARD_LOADED",
        "missing_artifacts": missing,
        "artifacts": artifacts,
        "dashboard": artifacts["dashboard_json"]["json"],
        "dashboard_markdown": artifacts["dashboard_md"]["text"],
        "dashboard_html": artifacts["dashboard_html"]["text"],
        "claim_boundary": artifacts["claim_boundary"]["text"],
        "source_redaction": artifacts["redaction_report"]["json"],
        "network_used": False,
        "raw_private_data_inspected": False,
    }
