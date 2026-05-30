from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


CLAIM_AUDIT_PATH = Path("pilot_dashboard") / "ROE21_DASHBOARD_REFRESH_CLAIM_AUDIT.json"

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
    re.compile(r"\bskipped\s+candidates?\s+succeeded\b", re.I),
]
SAFE_CONTEXT = ["not ", "no ", "do not", "does not", "cannot ", "without ", "must not", "claim boundary", "must_not_claim", "known limits"]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def scan_dashboard_refresh_claims(paths: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        full = _repo_root() / path
        if not full.exists() or not full.is_file():
            continue
        lines = full.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            if any(marker in lowered for marker in SAFE_CONTEXT):
                continue
            previous = "\n".join(lines[max(0, line_number - 12) : line_number]).lower()
            if "what this is not" in previous or "claim boundary" in previous or "must_not_claim" in previous or "must not" in previous:
                continue
            for pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append({"path": str(path).replace("\\", "/"), "line": line_number, "pattern": pattern.pattern})
                    break
    return findings


def run_dashboard_refresh_claim_audit(paths: list[Path], write_result: bool = True) -> dict[str, Any]:
    findings = scan_dashboard_refresh_claims(paths)
    result = {
        "schema": "ResidualOps_DashboardRefreshClaimAudit/v0.1",
        "generated_at": timestamp(),
        "decision": "BLOCK_OVERCLAIM" if findings else "PASS_CLAIM_BOUNDARY_CLEAN",
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "external_action_authorized": False,
    }
    if write_result:
        _write_json(CLAIM_AUDIT_PATH, result)
    return result
