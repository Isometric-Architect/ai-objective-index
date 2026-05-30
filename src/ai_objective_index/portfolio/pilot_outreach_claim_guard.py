from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ai_objective_index.real_pypi_upload_gate import _repo_root

from .pilot_discovery_personas import OUTREACH_DIR, timestamp


CLAIM_AUDIT_PATH = OUTREACH_DIR / "PILOT_OUTREACH_CLAIM_AUDIT.json"
REDACTION_REPORT_PATH = OUTREACH_DIR / "PILOT_OUTREACH_REDACTION_REPORT.json"

OUTREACH_SUFFIXES = {".md", ".json", ".txt"}

RISKY_PATTERNS = [
    re.compile(r"\bsecurity\s+certified\b", re.I),
    re.compile(r"\bcertified\s+safe\b", re.I),
    re.compile(r"\bquality\s+guaranteed\b", re.I),
    re.compile(r"\bproduction[-\s]+ready\b", re.I),
    re.compile(r"\blegal\s+compliance\b", re.I),
    re.compile(r"\bprivacy\s+compliant\b", re.I),
    re.compile(r"\blicense\s+cleared\b", re.I),
    re.compile(r"\beval[-\s]+clean\s+proven\b", re.I),
    re.compile(r"\bcode\s+correctness\s+proven\b", re.I),
    re.compile(r"\baction\s+authorized\b", re.I),
    re.compile(r"\bautonomous\s+action\b", re.I),
    re.compile(r"\blive\s+deployment\b", re.I),
    re.compile(r"\bofficial\s+standard\b", re.I),
    re.compile(r"\ball\s+agents\s+should\s+use\b", re.I),
]
SAFE_CONTEXT = [
    "not ",
    "no ",
    "do not",
    "does not",
    "cannot ",
    "must not",
    "blocked",
    "forbidden",
    "avoid",
    "claim boundary",
    "known limits",
    "must_not_claim",
]

REDACTION_PATTERNS = [
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}\b")),
    ("github_token", re.compile(r"\bghp_[A-Za-z0-9_]{12,}\b")),
    ("huggingface_token", re.compile(r"\bhf_[A-Za-z0-9]{12,}\b")),
    ("bearer_token", re.compile(r"\bbearer\s+[A-Za-z0-9_\-.]{16,}\b", re.I)),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("env_content", re.compile(r"^\s*[A-Z0-9_]{3,}\s*=\s*[^<\s].{8,}$", re.I)),
    ("email_or_phone", re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b|\b\d{3}[-.]\d{3}[-.]\d{4}\b", re.I)),
    ("private_kernel_value", re.compile(r"\b(weights?|thresholds?|provider priors?|private negative controls?)\s*[:=]\s*\d", re.I)),
    ("credential_wording", re.compile(r"\b(live credential|raw private data|raw pii)\s*[:=]\s*[^<\s].{4,}", re.I)),
]
REDACTED_CONTEXT = ["todo", "placeholder", "redacted", "example", "do not", "avoid", "must not", "no "]


def _candidate_paths(paths: list[Path] | None = None) -> list[Path]:
    root = _repo_root()
    if paths is not None:
        return paths
    directory = root / OUTREACH_DIR
    if not directory.exists():
        return []
    return sorted(path.relative_to(root) for path in directory.glob("*") if path.is_file() and path.suffix.lower() in OUTREACH_SUFFIXES)


def _safe_line(line: str, previous: list[str] | None = None) -> bool:
    lowered = line.lower()
    if any(marker in lowered for marker in SAFE_CONTEXT):
        return True
    context = "\n".join(previous or []).lower()
    return any(marker in context for marker in ["do not say", "must not claim", "must_not_claim", "blocked", "what this is not", "claim boundary"])


def scan_outreach_claim_text(text: str, label: str = "<memory>") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    lines = text.splitlines()
    for line_number, line in enumerate(lines, start=1):
        if _safe_line(line, lines[max(0, line_number - 10) : line_number - 1]):
            continue
        for pattern in RISKY_PATTERNS:
            if pattern.search(line):
                findings.append({"label": label, "line": line_number, "finding_type": "overclaim", "pattern": pattern.pattern})
                break
    return findings


def run_outreach_claim_audit(paths: list[Path] | None = None, write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    findings: list[dict[str, Any]] = []
    for path in _candidate_paths(paths):
        full = root / path
        if full.exists():
            findings.extend(scan_outreach_claim_text(full.read_text(encoding="utf-8", errors="ignore"), str(path).replace("\\", "/")))
    result = {
        "schema": "ResidualOps_PilotOutreachClaimAudit/v0.1",
        "generated_at": timestamp(),
        "decision": "BLOCK_OVERCLAIM" if findings else "PASS_OUTREACH_CLAIM_BOUNDARY_CLEAN",
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "allowed_language": [
            "static demo",
            "local artifact",
            "feedback request",
            "claim boundary",
            "ALLOW/HOLD/BLOCK",
            "not certification",
            "no external action",
        ],
    }
    if write_result:
        destination = root / CLAIM_AUDIT_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def _is_redacted(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in REDACTED_CONTEXT)


def scan_outreach_redaction_text(text: str, label: str = "<memory>") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for name, pattern in REDACTION_PATTERNS:
            if pattern.search(line) and not _is_redacted(line):
                findings.append({"label": label, "line": line_number, "finding_type": name, "severity": "block"})
                break
    return findings


def run_outreach_redaction(paths: list[Path] | None = None, write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    findings: list[dict[str, Any]] = []
    for path in _candidate_paths(paths):
        full = root / path
        if full.exists():
            findings.extend(scan_outreach_redaction_text(full.read_text(encoding="utf-8", errors="ignore"), str(path).replace("\\", "/")))
    result = {
        "schema": "ResidualOps_PilotOutreachRedactionReport/v0.1",
        "generated_at": timestamp(),
        "decision": "BLOCK_SENSITIVE_CONTENT" if findings else "PASS_REDACTED",
        "finding_count": len(findings),
        "findings": findings[:100],
        "token_printed": False,
        "private_kernel_exposed": any(item["finding_type"] == "private_kernel_value" for item in findings),
        "auto_send_performed": False,
        "external_api_used": False,
    }
    if write_result:
        destination = root / REDACTION_REPORT_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
