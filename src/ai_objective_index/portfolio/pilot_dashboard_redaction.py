from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


REDACTION_REPORT_PATH = Path("pilot_dashboard") / "RESIDUALOPS_PILOT_DASHBOARD_REDACTION_REPORT.json"

TOKEN_PATTERNS = [
    re.compile(r"\bpypi-[A-Za-z0-9_\-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
]
PRIVATE_KERNEL_PATTERNS = [
    re.compile(r"\b(private\s+ranking\s+weights?|exact\s+ranking\s+weights?|threshold\s+policy|provider\s+trust\s+prior)\s*[:=]\s*\d", re.I),
    re.compile(r"\b(private\s+negative-control\s+seed|private\s+probe\s+seed|commercial\s+routing\s+policy)\s*[:=]", re.I),
]
PII_PATTERNS = [
    re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b"),
]
RAW_ROW_PATTERN = re.compile(r"^[A-Za-z0-9_\- ]{1,80},[A-Za-z0-9_\- .@]{1,120},[A-Za-z0-9_\- .@]{1,120}(?:,|$)")


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _scan_text(text: str, label: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(pattern.search(line) for pattern in TOKEN_PATTERNS):
            findings.append({"label": label, "line": line_number, "finding_type": "token_or_secret"})
            continue
        if ".env" in line and "=" in line:
            findings.append({"label": label, "line": line_number, "finding_type": "env_content"})
            continue
        if any(pattern.search(line) for pattern in PRIVATE_KERNEL_PATTERNS):
            findings.append({"label": label, "line": line_number, "finding_type": "private_kernel_value"})
            continue
        if any(pattern.search(line) for pattern in PII_PATTERNS):
            findings.append({"label": label, "line": line_number, "finding_type": "personal_data"})
            continue
        if RAW_ROW_PATTERN.search(line) and "raw_dataset" in label.lower():
            findings.append({"label": label, "line": line_number, "finding_type": "raw_dataset_row"})
    return findings


def scan_dashboard_payload(payload: Any, label: str = "dashboard_payload") -> dict[str, Any]:
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str) if not isinstance(payload, str) else payload
    findings = _scan_text(text, label)
    block_count = len([finding for finding in findings if finding["finding_type"] in {"token_or_secret", "env_content", "private_kernel_value"}])
    hold_count = len(findings) - block_count
    decision = "BLOCK_SENSITIVE_CONTENT" if block_count else "HOLD_REVIEW_RECOMMENDED" if hold_count else "PASS_REDACTED"
    return {
        "schema": "ResidualOps_PilotDashboardRedactionReport/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "label": label,
        "finding_count": len(findings),
        "block_count": block_count,
        "hold_count": hold_count,
        "findings": findings,
        "redaction_applied": False,
        "token_printed": False,
        "private_kernel_exposed": block_count > 0,
    }


def scan_dashboard_artifacts(paths: list[Path], write_result: bool = True) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        full = _repo_root() / path
        if full.exists() and full.is_file():
            findings.extend(_scan_text(full.read_text(encoding="utf-8", errors="ignore"), str(path).replace("\\", "/")))
    block_count = len([finding for finding in findings if finding["finding_type"] in {"token_or_secret", "env_content", "private_kernel_value"}])
    hold_count = len(findings) - block_count
    report = {
        "schema": "ResidualOps_PilotDashboardRedactionReport/v0.1",
        "generated_at": _timestamp(),
        "decision": "BLOCK_SENSITIVE_CONTENT" if block_count else "HOLD_REVIEW_RECOMMENDED" if hold_count else "PASS_REDACTED",
        "artifact_count": len(paths),
        "finding_count": len(findings),
        "block_count": block_count,
        "hold_count": hold_count,
        "findings": findings,
        "redaction_applied": False,
        "token_printed": False,
        "private_kernel_exposed": block_count > 0,
    }
    if write_result:
        _write_json(REDACTION_REPORT_PATH, report)
    return report
