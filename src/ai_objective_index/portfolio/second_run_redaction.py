from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


SECOND_RUN_DIR = Path("pilot_second_runs")
REDACTION_REPORT_PATH = SECOND_RUN_DIR / "ROE15_SECOND_RUN_REDACTION_REPORT.json"

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
    re.compile(r"\b(?:\+?\d{1,3}[-. ]?)?\d{3}[-.]\d{3}[-.]\d{4}\b"),
]
RAW_DATASET_ROW_PATTERN = re.compile(r"(?i)\b(name|email|phone|address|ssn|birth|dob)\b\s*,\s*[^,\n]{1,120}\s*,\s*[^,\n]{1,120}")


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
        if RAW_DATASET_ROW_PATTERN.search(line):
            findings.append({"label": label, "line": line_number, "finding_type": "raw_dataset_row"})
            continue
        if any(pattern.search(line) for pattern in PII_PATTERNS):
            findings.append({"label": label, "line": line_number, "finding_type": "personal_data"})
    return findings


def scan_second_run_payload(payload: Any, label: str = "second_run_payload") -> dict[str, Any]:
    text = payload if isinstance(payload, str) else json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    findings = _scan_text(text, label)
    return _build_report(findings, artifact_count=1, label=label)


def _build_report(findings: list[dict[str, Any]], artifact_count: int, label: str = "second_run_artifacts") -> dict[str, Any]:
    block_types = {"token_or_secret", "env_content", "private_kernel_value", "raw_dataset_row"}
    block_count = len([finding for finding in findings if finding["finding_type"] in block_types])
    hold_count = len(findings) - block_count
    return {
        "schema": "ResidualOps_SecondRunRedactionReport/v0.1",
        "generated_at": _timestamp(),
        "decision": "BLOCK_SENSITIVE_CONTENT" if block_count else "HOLD_REVIEW_RECOMMENDED" if hold_count else "PASS_REDACTED",
        "label": label,
        "artifact_count": artifact_count,
        "finding_count": len(findings),
        "block_count": block_count,
        "hold_count": hold_count,
        "findings": findings,
        "redaction_applied": False,
        "token_printed": False,
        "private_kernel_exposed": any(finding["finding_type"] == "private_kernel_value" for finding in findings),
    }


def scan_second_run_artifacts(paths: list[Path], write_result: bool = True) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        full = _repo_root() / path
        if full.exists() and full.is_file():
            findings.extend(_scan_text(full.read_text(encoding="utf-8", errors="ignore"), str(path).replace("\\", "/")))
    report = _build_report(findings, artifact_count=len(paths))
    if write_result:
        _write_json(REDACTION_REPORT_PATH, report)
    return report
