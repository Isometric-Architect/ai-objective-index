from __future__ import annotations

import re
from pathlib import Path
from typing import Any


MUST_NOT_CLAIM = [
    "candidate is verified",
    "metadata proves correctness",
    "tool availability authorizes tool use",
    "source trace is security certification",
    "route decision authorizes external action",
    "AOI clears legal, privacy, license, or compliance status",
    "AOI proves product readiness or quality",
]

CLAIM_BOUNDARY = [
    "candidate != verified",
    "metadata != proof",
    "tool_available != tool_authorized",
    "source_trace != security_certification",
    "route_decision != action_authorization",
]

RISKY_PHRASES = [
    "security certified",
    "certified safe",
    "safe tool",
    "code correctness proven",
    "legal compliance",
    "privacy compliant",
    "license cleared",
    "eval-clean proven",
    "production ready",
    "production-ready",
    "quality guaranteed",
    "action authorized",
    "merge authorized",
    "deploy authorized",
    "training authorized",
    "official standard",
    "all agents should use",
]

NEGATING_CONTEXT = [
    "not ",
    "not a",
    "not an",
    "no ",
    "does not",
    "do not",
    "must not",
    "never",
    "without",
    "claim boundary",
    "must_not_claim",
    "forbidden",
]

PRIVATE_KERNEL_VALUE_PATTERNS = [
    re.compile(r"\b(ranking weights?|exact weights?|thresholds?|provider priors?|anti-gaming rules?)\b\s*[:=]\s*[-0-9.]+", re.I),
    re.compile(r"\b(private negative controls?|private probe seeds?|commercial routing policy)\b\s*[:=]\s*[-0-9.]+", re.I),
    re.compile(r"\b(private kernel|hidden decision kernel)\b\s*[:=]\s*[-0-9.]+", re.I),
]


def is_negated(lines: list[str], index: int) -> bool:
    window = " ".join(lines[max(0, index - 4) : index + 2]).lower()
    return any(marker in window for marker in NEGATING_CONTEXT)


def scan_text_for_overclaims(text: str, path: str = "<memory>") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        lowered = line.lower()
        for phrase in RISKY_PHRASES:
            if phrase in lowered and not is_negated(lines, index):
                findings.append({"kind": "overclaim", "path": path, "line": index + 1, "phrase": phrase, "text": line.strip()[:180]})
        for pattern in PRIVATE_KERNEL_VALUE_PATTERNS:
            if pattern.search(line):
                findings.append({"kind": "private_kernel_value", "path": path, "line": index + 1, "phrase": pattern.pattern, "text": line.strip()[:180]})
    return findings


def scan_paths(paths: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".json", ".txt", ".py"}:
            continue
        findings.extend(scan_text_for_overclaims(path.read_text(encoding="utf-8", errors="ignore"), str(path)))
    return findings

