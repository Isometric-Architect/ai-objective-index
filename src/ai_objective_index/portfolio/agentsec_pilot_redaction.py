from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import TOKEN_PATTERNS


PRIVATE_KERNEL_PATTERNS = [
    re.compile(r"\bprovider\s+trust\s+prior\s*[:=]\s*\d", re.I),
    re.compile(r"\bprivate\s+ranking\s+weights?\s*[:=]\s*\d", re.I),
    re.compile(r"\bthreshold\s+policy\s*[:=]\s*\d", re.I),
    re.compile(r"\bprivate\s+negative-control\s+seed\s*[:=]", re.I),
    re.compile(r"\bcommercial\s+routing\s+policy\s*[:=]\s*\d", re.I),
]

PII_REVIEW_PATTERNS = [
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"\b\+?\d[\d .()-]{8,}\d\b"),
]

PRIVATE_KEY_PATTERN = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def text_from_payload(payload: Any) -> str:
    if isinstance(payload, str):
        return payload
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)


def redact_text(text: str) -> tuple[str, bool]:
    redacted = text
    changed = False
    for pattern in TOKEN_PATTERNS:
        redacted, count = pattern.subn("[redacted-token]", redacted)
        changed = changed or count > 0
    redacted, count = PRIVATE_KEY_PATTERN.subn("[redacted-private-key]", redacted)
    changed = changed or count > 0
    return redacted, changed


def scan_payload(payload: Any, label: str = "<memory>") -> dict[str, Any]:
    text = text_from_payload(payload)
    redacted, changed = redact_text(text)
    findings: list[dict[str, Any]] = []
    for pattern in TOKEN_PATTERNS:
        if pattern.search(text):
            findings.append({"severity": "BLOCK", "kind": "token_like", "label": label, "pattern": pattern.pattern})
    if PRIVATE_KEY_PATTERN.search(text):
        findings.append({"severity": "BLOCK", "kind": "private_key", "label": label, "pattern": PRIVATE_KEY_PATTERN.pattern})
    for pattern in PRIVATE_KERNEL_PATTERNS:
        if pattern.search(text):
            findings.append({"severity": "BLOCK", "kind": "private_kernel_value", "label": label, "pattern": pattern.pattern})
    for pattern in PII_REVIEW_PATTERNS:
        if pattern.search(text):
            findings.append({"severity": "HOLD", "kind": "possible_personal_data", "label": label, "pattern": pattern.pattern})

    block_count = sum(1 for finding in findings if finding["severity"] == "BLOCK")
    hold_count = sum(1 for finding in findings if finding["severity"] == "HOLD")
    if block_count:
        decision = "BLOCK_SENSITIVE_CONTENT"
    elif hold_count:
        decision = "HOLD_REVIEW_RECOMMENDED"
    else:
        decision = "PASS_REDACTED"
    return {
        "schema": "ResidualOps_AgentSecPilotRedactionReport/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "label": label,
        "finding_count": len(findings),
        "block_count": block_count,
        "hold_count": hold_count,
        "findings": findings[:100],
        "redaction_applied": changed,
        "token_printed": False,
        "private_kernel_exposed": block_count > 0,
    }


def scan_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return scan_payload(text, str(path).replace("\\", "/"))
