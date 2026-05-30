from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root


REPLY_DIR = Path("feedback_replies")
REDACTION_REPORT_PATH = REPLY_DIR / "FEEDBACK_REPLY_REDACTION_REPORT.json"

TOKEN_PATTERNS = [
    ("token_or_secret", re.compile(r"\bpypi-[A-Za-z0-9_\-]{20,}\b")),
    ("token_or_secret", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("token_or_secret", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b")),
    ("token_or_secret", re.compile(r"\bbearer\s+[A-Za-z0-9_\-.]{16,}\b", re.I)),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
]
HOLD_PATTERNS = [
    ("personal_data", re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")),
    ("personal_data", re.compile(r"\b(?:\+?\d{1,3}[-. ]?)?\d{3}[-.]\d{3}[-.]\d{4}\b")),
]
BLOCK_PATTERNS = [
    ("env_content", re.compile(r"^\s*[A-Z0-9_]{3,}\s*=\s*[^<\s].{8,}$", re.I)),
    ("raw_private_dataset_row", re.compile(r"(?i)\b(name|email|phone|address|ssn|birth|dob)\b\s*,\s*[^,\n]{1,120}\s*,\s*[^,\n]{1,120}")),
    ("private_kernel_value", re.compile(r"\b(weights?|thresholds?|provider\s+priors?|private negative controls?)\s*[:=]\s*\d", re.I)),
    ("private_kernel_value", re.compile(r"\b(private\s+probe\s+seed|commercial\s+routing\s+policy)\s*[:=]", re.I)),
    ("live_url_secret", re.compile(r"https?://\S+(?:token|key|secret|password)=", re.I)),
]


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def scan_feedback_reply_text(text: str, label: str = "<memory>") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for finding_type, pattern in TOKEN_PATTERNS + BLOCK_PATTERNS + HOLD_PATTERNS:
            if pattern.search(line):
                severity = "hold" if finding_type == "personal_data" else "block"
                findings.append({"label": label, "line": line_number, "finding_type": finding_type, "severity": severity})
                break
    return findings


def redact_reply_text(text: str) -> tuple[str, list[dict[str, Any]]]:
    findings = scan_feedback_reply_text(text)
    redacted = text
    for _finding_type, pattern in TOKEN_PATTERNS + BLOCK_PATTERNS + HOLD_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted, findings


def build_redaction_report(findings: list[dict[str, Any]], artifact_count: int = 1) -> dict[str, Any]:
    block_count = len([item for item in findings if item.get("severity") == "block"])
    hold_count = len(findings) - block_count
    return {
        "schema": "ResidualOps_FeedbackReplyRedactionReport/v0.1",
        "generated_at": timestamp(),
        "decision": "BLOCK_SENSITIVE_CONTENT" if block_count else "HOLD_REVIEW_RECOMMENDED" if hold_count else "PASS_REDACTED",
        "artifact_count": artifact_count,
        "finding_count": len(findings),
        "block_count": block_count,
        "hold_count": hold_count,
        "findings": findings[:100],
        "token_printed": False,
        "private_kernel_exposed": any(item["finding_type"] == "private_kernel_value" for item in findings),
        "auto_send_performed": False,
        "external_api_used": False,
        "external_action_performed": False,
    }


def scan_reply_artifacts(paths: list[Path], write_result: bool = True) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        full = _repo_root() / path
        if full.exists() and full.is_file():
            findings.extend(scan_feedback_reply_text(full.read_text(encoding="utf-8", errors="ignore"), str(path).replace("\\", "/")))
    report = build_redaction_report(findings, artifact_count=len(paths))
    if write_result:
        _write_json(REDACTION_REPORT_PATH, report)
    return report
