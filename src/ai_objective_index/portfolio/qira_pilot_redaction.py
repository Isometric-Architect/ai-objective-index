from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import Any


TOKEN_PATTERNS = [
    re.compile(r"\bpypi-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9._-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
]

PRIVATE_KERNEL_PATTERNS = [
    re.compile(r"\bprivate\s+ranking\s+weights?\s*[:=]\s*\d", re.I),
    re.compile(r"\bprovider\s+trust\s+prior\s*[:=]\s*\d", re.I),
    re.compile(r"\banti-gaming\s+threshold\s*[:=]\s*\d", re.I),
    re.compile(r"\bprivate\s+negative-control\s+seed\s*[:=]", re.I),
    re.compile(r"\bcommercial\s+routing\s+policy\s*[:=]\s*\d", re.I),
]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _as_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)


def scan_payload(payload: Any, label: str = "qira-pilot") -> dict[str, Any]:
    text = _as_text(payload)
    findings: list[dict[str, str]] = []
    for pattern in TOKEN_PATTERNS:
        if pattern.search(text):
            findings.append({"finding_type": "secret_or_token", "pattern": pattern.pattern})
    for pattern in PRIVATE_KERNEL_PATTERNS:
        if pattern.search(text):
            findings.append({"finding_type": "private_kernel", "pattern": pattern.pattern})
    block_count = len(findings)
    decision = "BLOCK_SENSITIVE_CONTENT" if block_count else "PASS_REDACTED"
    return {
        "schema": "ResidualOps_QIRAPilotRedactionReport/v0.1",
        "generated_at": _timestamp(),
        "decision": decision,
        "label": label,
        "finding_count": len(findings),
        "block_count": block_count,
        "hold_count": 0,
        "findings": findings,
        "redaction_applied": False,
        "token_printed": False,
        "private_kernel_exposed": any(finding["finding_type"] == "private_kernel" for finding in findings),
    }
