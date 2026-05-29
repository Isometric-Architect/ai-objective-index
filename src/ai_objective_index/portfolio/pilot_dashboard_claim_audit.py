from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


CLAIM_AUDIT_PATH = Path("public_launch") / "roe16" / "ROE16_DASHBOARD_CLAIM_AUDIT.json"

RISKY_PATTERNS = [
    re.compile(r"\bsecurity\s+certified\b", re.I),
    re.compile(r"\bsafe\s+tool\b", re.I),
    re.compile(r"\bcode\s+correctness\s+proven\b", re.I),
    re.compile(r"\blegal\s+compliance\b", re.I),
    re.compile(r"\bprivacy\s+compliant\b", re.I),
    re.compile(r"\blicense\s+cleared\b", re.I),
    re.compile(r"\beval[-\s]+clean\s+proven\b", re.I),
    re.compile(r"\bproduction\s+ready\b", re.I),
    re.compile(r"\bquality\s+guaranteed\b", re.I),
    re.compile(r"\baction\s+authorized\b", re.I),
    re.compile(r"\bmerge\s+authorized\b", re.I),
    re.compile(r"\bdeploy\s+authorized\b", re.I),
    re.compile(r"\btraining\s+authorized\b", re.I),
    re.compile(r"\bexternal\s+pilot\s+completed\b", re.I),
]
SAFE_CONTEXT = ["not ", "no ", "do not", "does not", "cannot ", "without ", "must not", "must_not_claim", "known limits", "claim boundary"]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def scan_dashboard_claim_text(text: str, label: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    lines = text.splitlines()
    for line_number, line in enumerate(lines, start=1):
        lowered = line.lower()
        if any(marker in lowered for marker in SAFE_CONTEXT):
            continue
        previous = "\n".join(lines[max(0, line_number - 6) : line_number]).lower()
        if "what this is not" in previous or "claim boundaries" in previous or "known limits" in previous:
            continue
        for pattern in RISKY_PATTERNS:
            if pattern.search(line):
                findings.append({"label": label, "line": line_number, "finding_type": "overclaim", "pattern": pattern.pattern})
                break
    return findings


def run_dashboard_claim_audit(paths: list[Path] | None = None, write_result: bool = True) -> dict[str, Any]:
    paths = paths or [
        Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.json",
        Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.md",
        Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD.html",
        Path("pilot_dashboard") / "RESIDUALOPS_PILOT_CLAIM_BOUNDARY.md",
        Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD_KNOWN_LIMITS.md",
        Path("docs") / "portfolio" / "roe16_pilot_dashboard_artifact_pack.md",
        Path("docs") / "portfolio" / "pilot_dashboard_workflow.md",
        Path("docs") / "portfolio" / "pilot_dashboard_static_html.md",
        Path("docs") / "portfolio" / "pilot_dashboard_claim_boundaries.md",
        Path("docs") / "portfolio" / "pilot_dashboard_operator_checklist.md",
    ]
    findings: list[dict[str, Any]] = []
    for path in paths:
        full = _repo_root() / path
        if full.exists() and full.is_file():
            findings.extend(scan_dashboard_claim_text(full.read_text(encoding="utf-8", errors="ignore"), str(path).replace("\\", "/")))
    result = {
        "schema": "ResidualOps_PilotDashboardClaimAudit/v0.1",
        "generated_at": _timestamp(),
        "decision": "BLOCK_OVERCLAIM" if findings else "PASS_CLAIM_BOUNDARY_CLEAN",
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "allowed_language": [
            "static dashboard artifact",
            "local dry-run",
            "local receipt",
            "claim boundary",
            "ALLOW/HOLD/BLOCK",
            "feedback memory",
            "known limits",
            "not certification",
        ],
    }
    if write_result:
        _write_json(CLAIM_AUDIT_PATH, result)
    return result
