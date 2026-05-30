from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_refresh_manifest import SHARE_V2_DIR, timestamp


CLAIM_AUDIT_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_CLAIM_AUDIT_V2.json"

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
    re.compile(r"\blive\s+connector\s+ready\b", re.I),
    re.compile(r"\bproduct\s+ready\s+badge\b", re.I),
    re.compile(r"\bqleos\s+compatible\s+badge\b", re.I),
    re.compile(r"\bskipped\s+candidates?\s+succeeded\b", re.I),
    re.compile(r"\ball\s+feedback\s+resolved\b", re.I),
]
SAFE_CONTEXT = ["not ", "no ", "do not", "does not", "cannot ", "without ", "must not", "must_not_claim", "known limits", "claim boundary", "blocked"]


def scan_refresh_claim_text(text: str, label: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    lines = text.splitlines()
    for line_number, line in enumerate(lines, start=1):
        lowered = line.lower()
        if any(marker in lowered for marker in SAFE_CONTEXT):
            continue
        previous = "\n".join(lines[max(0, line_number - 8) : line_number]).lower()
        if "what this is not" in previous or "claim boundary" in previous or "known limits" in previous:
            continue
        for pattern in RISKY_PATTERNS:
            if pattern.search(line):
                findings.append({"label": label, "line": line_number, "finding_type": "overclaim", "pattern": pattern.pattern})
                break
    return findings


def run_refresh_claim_audit(paths: list[Path] | None = None, write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    if paths is None:
        paths = sorted(path.relative_to(root) for path in (root / SHARE_V2_DIR).glob("*") if path.is_file())
    findings: list[dict[str, Any]] = []
    for path in paths:
        full = root / path
        if full.exists() and full.is_file():
            findings.extend(scan_refresh_claim_text(full.read_text(encoding="utf-8", errors="ignore"), str(path).replace("\\", "/")))
    result = {
        "schema": "ResidualOps_ExternalShareRefreshClaimAudit/v0.1",
        "generated_at": timestamp(),
        "decision": "BLOCK_OVERCLAIM" if findings else "PASS_CLAIM_BOUNDARY_CLEAN",
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "allowed_language": [
            "static local demo",
            "feedback second-run bridge",
            "skipped candidate",
            "HOLD_NEEDS_ARTIFACT",
            "known limits",
            "not certification",
            "no external action",
        ],
    }
    if write_result:
        destination = root / CLAIM_AUDIT_V2_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
