from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_PATH = Path("data/generated/no_secrets_audit_result_v0_2.json")

SCAN_ROOTS = [
    "README.md",
    "docs",
    "examples",
    "hf_demo",
    "hf_dataset",
    "release/public_beta_v0_2",
    "launch/manual_public_beta_v0_2",
]

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".jsonl",
    ".py",
    ".js",
    ".toml",
    ".yaml",
    ".yml",
}

EXCLUDED_FILE_NAMES = {
    "NO_SECRETS_AUDIT_RESULT.json",
}

SECRET_PATTERNS = [
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}\b")),
    ("github_token", re.compile(r"\bghp_[A-Za-z0-9_]{12,}\b")),
    ("huggingface_token", re.compile(r"\bhf_[A-Za-z0-9]{12,}\b")),
    ("slack_token", re.compile(r"\bxoxb-[A-Za-z0-9\-]{12,}\b")),
    ("api_key_assignment", re.compile(r"\bapi_key\s*=\s*[\"']?[^\"'\s]{8,}", re.IGNORECASE)),
    ("password_assignment", re.compile(r"\bpassword\s*=\s*[\"']?[^\"'\s]{6,}", re.IGNORECASE)),
    ("bearer_token", re.compile(r"\bbearer\s+[A-Za-z0-9_\-\.]{16,}\b", re.IGNORECASE)),
    ("private_key", re.compile(r"PRIVATE KEY")),
    ("aws_access_key", re.compile(r"\bAWS_ACCESS_KEY_ID\b")),
    ("aws_secret_key", re.compile(r"\bAWS_SECRET_ACCESS_KEY\b")),
]

REDACTED_MARKERS = [
    "redacted",
    "placeholder",
    "example",
    "<",
    "xxxx",
    "your_",
    "dummy",
    "not a real",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _iter_files(scan_roots: list[str | Path] | None = None) -> list[Path]:
    root = _repo_root()
    files: list[Path] = []
    for entry in scan_roots or SCAN_ROOTS:
        path = Path(entry)
        if not path.is_absolute():
            path = root / path
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in TEXT_SUFFIXES:
                    if child.name in EXCLUDED_FILE_NAMES:
                        continue
                    if any(part in {".git", "__pycache__", ".pytest_cache"} for part in child.parts):
                        continue
                    files.append(child)
    return sorted(set(files))


def _is_redacted(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in REDACTED_MARKERS)


def scan_text_for_secrets(text: str, file_label: str = "<memory>") -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for name, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(line):
                item = {
                    "file": file_label,
                    "line": line_no,
                    "pattern": name,
                    "match_preview": match.group(0)[:12] + "...",
                    "text": line.strip()[:160],
                }
                if _is_redacted(line):
                    warnings.append({**item, "severity": "warning", "redacted_or_example": True})
                else:
                    findings.append({**item, "severity": "block", "redacted_or_example": False})
    return {"findings": findings, "warnings": warnings}


def run_no_secrets_audit(scan_roots: list[str | Path] | None = None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    scanned_files: list[str] = []
    for path in _iter_files(scan_roots):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(path.relative_to(_repo_root())) if _repo_root() in path.parents else str(path)
        scanned_files.append(rel)
        result = scan_text_for_secrets(text, rel)
        findings.extend(result["findings"])
        warnings.extend(result["warnings"])

    overall = "BLOCK" if findings else ("HOLD" if warnings else "PASS")
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": overall,
        "finding_count": len(findings),
        "warning_count": len(warnings),
        "findings": findings,
        "warnings": warnings,
        "scanned_file_count": len(scanned_files),
        "scanned_files": scanned_files,
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }


def save_no_secrets_audit(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    payload = results or run_no_secrets_audit()
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    results = run_no_secrets_audit()
    path = save_no_secrets_audit(results)
    print(f"Saved no-secrets audit: {path}")
    print(
        "no_secrets_audit: "
        f"{results['overall_token']} "
        f"findings={results['finding_count']} "
        f"warnings={results['warning_count']} "
        "live_network_used=False"
    )


if __name__ == "__main__":
    main()
