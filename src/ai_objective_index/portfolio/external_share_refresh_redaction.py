from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .external_share_refresh_manifest import SHARE_V2_DIR, timestamp


REDACTION_V2_PATH = SHARE_V2_DIR / "RESIDUALOPS_EXTERNAL_SAFE_REDACTION_REPORT_V2.json"

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
RAW_ROW_PATTERN = re.compile(r"^[A-Za-z0-9_\- ]{1,80},[A-Za-z0-9_\- .@]{1,120},[A-Za-z0-9_\- .@]{1,120}(?:,|$)")
UNSAFE_FILE_PATTERN = re.compile(r"(mcp-publisher\.exe|\.whl$|\.tar\.gz$|^dist/)", re.I)


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


def scan_refresh_payload(payload: Any, label: str = "refresh_payload") -> dict[str, Any]:
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str) if not isinstance(payload, str) else payload
    return build_redaction_report(_scan_text(text, label), artifact_count=1)


def build_redaction_report(findings: list[dict[str, Any]], artifact_count: int) -> dict[str, Any]:
    block_types = {"token_or_secret", "env_content", "private_kernel_value", "unsafe_file"}
    block_count = len([finding for finding in findings if finding["finding_type"] in block_types])
    hold_count = len(findings) - block_count
    return {
        "schema": "ResidualOps_ExternalShareRefreshRedactionReport/v0.1",
        "generated_at": timestamp(),
        "decision": "BLOCK_SENSITIVE_CONTENT" if block_count else "HOLD_REVIEW_RECOMMENDED" if hold_count else "PASS_REDACTED",
        "artifact_count": artifact_count,
        "finding_count": len(findings),
        "block_count": block_count,
        "hold_count": hold_count,
        "findings": findings[:100],
        "redaction_applied": False,
        "token_printed": False,
        "private_kernel_exposed": any(finding["finding_type"] == "private_kernel_value" for finding in findings),
    }


def scan_refresh_share_artifacts(paths: list[Path] | None = None, write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    if paths is None:
        paths = sorted(path.relative_to(root) for path in (root / SHARE_V2_DIR).glob("*") if path.is_file())
    findings: list[dict[str, Any]] = []
    for path in paths:
        rel = str(path).replace("\\", "/")
        if UNSAFE_FILE_PATTERN.search(rel):
            findings.append({"label": rel, "line": 0, "finding_type": "unsafe_file"})
            continue
        full = root / path
        if full.exists() and full.is_file():
            findings.extend(_scan_text(full.read_text(encoding="utf-8", errors="ignore"), rel))
    report = build_redaction_report(findings, artifact_count=len(paths))
    if write_result:
        destination = root / REDACTION_V2_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report
