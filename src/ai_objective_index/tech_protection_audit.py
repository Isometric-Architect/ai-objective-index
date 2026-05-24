from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from .real_pypi_upload_gate import TOKEN_PATTERNS, _repo_root


OUTPUT_PATH = Path("public_launch") / "wave12_tech_protection" / "TECH_PROTECTION_AUDIT_RESULT.json"

BLOCK_PATH_PATTERNS = [
    re.compile(r"(^|/)\.pypirc$", re.I),
    re.compile(r"(^|/)\.env(\.|$)", re.I),
    re.compile(r"(^|/)(source_0513|source_master|internal_source|raw_source_master)", re.I),
    re.compile(r"(^|/)(private_kernel|private_kernels|private_data|private_calibration|private_negative_controls|private_provider_priors)/", re.I),
]

SENSITIVE_PATTERNS = [
    re.compile(r"\b(exact|private|commercial|provider|anti-gaming|negative-control|probe bank|kernel)\b.{0,80}\b(weight|threshold|prior|seed|rule|heuristic|profile)\b\s*[:=]\s*[-0-9.]+", re.I),
    re.compile(r"\bprovider trust prior\b\s*[:=]\s*[-0-9.]+", re.I),
    re.compile(r"\bcommercial scoring profile\b\s*[:=]", re.I),
    re.compile(r"\bprivate negative-control seed\b\s*[:=]", re.I),
    re.compile(r"\bprivate probe bank\b\s*[:=]", re.I),
    re.compile(r"\banti-gaming heuristic\b\s*[:=]", re.I),
    re.compile(r"\bexploit\b.{0,50}\b(bypass|gaming recipe)\b", re.I),
    re.compile(r"\bprompt\b.{0,80}\b(hidden decision kernel|private kernel)\b", re.I),
]

HOLD_PATTERNS = [
    re.compile(r"\bexact ranking weights\b", re.I),
    re.compile(r"\bprivate ranking weights\b", re.I),
    re.compile(r"\bprivate dataset\b", re.I),
    re.compile(r"\banti-gaming logic\b", re.I),
]

SAFE_CONTEXT = [
    "do not expose",
    "must not expose",
    "not exposed",
    "remain private",
    "remains private",
    "should not be public",
    "private / should not be public",
    "placeholder",
    "template",
    "policy",
    "example scoring formula",
    "demo_profile_v0_1",
    "high-level",
    "public/private",
    "public-private",
    "allowed public",
    "not verified",
    "not security certified",
    "not a quality guarantee",
]

TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".jsonl",
    ".toml",
    ".yml",
    ".yaml",
    ".cfg",
    ".ini",
}


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _git_ls_files() -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-c", "safe.directory=C:/Users/Isometric-Architect/Desktop/ai_objective_index", "ls-files"],
            cwd=_repo_root(),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return []
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _safe_context(line: str) -> bool:
    lower = line.lower()
    return any(marker in lower for marker in SAFE_CONTEXT)


def _is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS and path.exists() and path.is_file() and path.stat().st_size <= 1_500_000


def scan_text_for_sensitive_disclosure(text: str, path: str = "<memory>") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    normalized_path = path.replace("\\", "/").lower()
    allow_test_token_fixtures = normalized_path.startswith("tests/")
    allow_test_private_kernel_fixtures = normalized_path.startswith("tests/")
    for index, line in enumerate(text.splitlines(), start=1):
        if _safe_context(line):
            continue
        for pattern in TOKEN_PATTERNS:
            if pattern.search(line):
                if allow_test_token_fixtures:
                    continue
                findings.append({"severity": "BLOCK", "kind": "token_or_secret", "path": path, "line": index, "pattern": pattern.pattern})
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(line):
                if allow_test_private_kernel_fixtures:
                    continue
                findings.append({"severity": "BLOCK", "kind": "private_kernel_detail", "path": path, "line": index, "pattern": pattern.pattern})
        for pattern in HOLD_PATTERNS:
            if pattern.search(line):
                if allow_test_private_kernel_fixtures:
                    continue
                findings.append({"severity": "HOLD", "kind": "review_sensitive_phrase", "path": path, "line": index, "pattern": pattern.pattern})
    return findings


def audit_paths(paths: Iterable[str]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    scanned_files = 0
    skipped_files = 0
    for relative in paths:
        normalized = relative.replace("\\", "/")
        for pattern in BLOCK_PATH_PATTERNS:
            if pattern.search(normalized):
                findings.append({"severity": "BLOCK", "kind": "sensitive_path", "path": normalized, "line": 0, "pattern": pattern.pattern})
        full = _repo_root() / relative
        if not _is_text_file(full):
            skipped_files += 1
            continue
        scanned_files += 1
        try:
            text = full.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            skipped_files += 1
            continue
        findings.extend(scan_text_for_sensitive_disclosure(text, normalized))

    block_findings = [item for item in findings if item["severity"] == "BLOCK"]
    hold_findings = [item for item in findings if item["severity"] == "HOLD"]
    if any(item["kind"] == "sensitive_path" and "source" in item["path"].lower() for item in block_findings):
        decision = "BLOCK_INTERNAL_SOURCE_LEAK"
    elif block_findings:
        decision = "BLOCK_SECRET_OR_PRIVATE_KERNEL_EXPOSED"
    elif hold_findings:
        decision = "HOLD_REVIEW_RECOMMENDED"
    else:
        decision = "PASS_NO_SENSITIVE_KERNEL_EXPOSED"
    return {
        "decision": decision,
        "scanned_files": scanned_files,
        "skipped_files": skipped_files,
        "findings": findings[:200],
        "finding_count": len(findings),
        "block_count": len(block_findings),
        "hold_count": len(hold_findings),
    }


def run_tech_protection_audit(write_result: bool = True) -> dict[str, Any]:
    payload = audit_paths(_git_ls_files())
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        **payload,
        "public_allowed": [
            "schemas",
            "API/MCP shapes",
            "high-level scoring component names",
            "source-trace methodology",
            "ALLOW/HOLD/BLOCK labels",
            "limitations",
            "sample/public_beta_mcp data",
        ],
        "private_must_not_expose": [
            "exact weights",
            "thresholds",
            "provider trust priors",
            "anti-gaming rules",
            "private negative-control seeds",
            "private probe bank",
            "commercial routing policy",
            "private operational datasets",
        ],
        "mcp_registry_submission_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_tech_protection_audit()
    print(f"tech_protection_audit: {result['decision']} findings={result['finding_count']}")


if __name__ == "__main__":
    main()
