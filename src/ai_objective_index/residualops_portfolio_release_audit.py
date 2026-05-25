from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root
from .residualops_portfolio_release_kit import OUTPUT_DIR, PORTFOLIO_KIT_PATH
from .residualops_public_private_alignment_audit import run_public_private_alignment_audit


AUDIT_PATH = OUTPUT_DIR / "ROE3_CLAIM_BOUNDARY_AUDIT.json"

RISKY_PATTERNS = [
    re.compile(r"\bverified\s+capability\b", re.I),
    re.compile(r"\bsafe\s+tool\b", re.I),
    re.compile(r"\bsecurity\s+certified\b", re.I),
    re.compile(r"\bquality\s+guaranteed\b", re.I),
    re.compile(r"\bproduction\s+ready\b", re.I),
    re.compile(r"\blegal\s+sufficiency\s+confirmed\b", re.I),
    re.compile(r"\bprivacy\s+compliant\b", re.I),
    re.compile(r"\blicense\s+cleared\b", re.I),
    re.compile(r"\beval\s+clean\b", re.I),
    re.compile(r"\baction\s+authorized\b", re.I),
    re.compile(r"\bexternal\s+action\s+authorization\b", re.I),
]

SAFE_CONTEXT = [
    "not ",
    "no ",
    "do not",
    "does not",
    "cannot ",
    "without ",
    "must not",
    "must_not_claim",
    "boundary",
    "claim",
]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _iter_files() -> list[Path]:
    root = _repo_root()
    candidates = [
        root / "README.md",
        root / "CHANGELOG.md",
        root / "docs" / "roe3_unified_portfolio_release_kit.md",
        root / "docs" / "residualops_portfolio_handoff.md",
        root / "docs" / "residualops_public_claim_boundaries.md",
        root / OUTPUT_DIR,
    ]
    files: list[Path] = []
    for path in candidates:
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}:
            files.append(path)
        elif path.is_dir():
            files.extend(child for child in path.rglob("*") if child.is_file() and child.suffix.lower() in {".md", ".json", ".txt"})
    return sorted(set(files))


def _safe_line(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in SAFE_CONTEXT)


def run_portfolio_release_audit(write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    findings: list[dict[str, Any]] = []
    for path in _iter_files():
        rel = str(path.relative_to(root)).replace("\\", "/")
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for index, line in enumerate(lines, start=1):
            if _safe_line(line):
                continue
            for pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append({"path": rel, "line": index, "pattern": pattern.pattern})
                    break
    alignment = run_public_private_alignment_audit(
        write_result=False,
        root=root,
        paths=[Path("docs"), OUTPUT_DIR, Path("README.md"), Path("CHANGELOG.md")],
    )
    kit = {}
    if (root / PORTFOLIO_KIT_PATH).exists():
        try:
            kit = json.loads((root / PORTFOLIO_KIT_PATH).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            kit = {}
    issues: list[str] = []
    if findings:
        issues.append("risky positive claims found")
    if alignment["decision"] != "PASS_PUBLIC_PRIVATE_ALIGNMENT":
        issues.append(f"public/private alignment {alignment['decision']}")
    for flag in ["external_actions_performed", "workflow_enabled", "network_used", "token_printed", "private_kernel_exposed"]:
        if kit.get(flag):
            issues.append(f"{flag} unexpectedly true")
    if any("PUBLIC_PRIVATE_LEAK" in issue for issue in issues):
        decision = "BLOCK_ROE3_PRIVATE_KERNEL_LEAK"
    elif findings or any("OVERCLAIM" in issue for issue in issues):
        decision = "BLOCK_ROE3_OVERCLAIM"
    elif issues:
        decision = "HOLD_ROE3_RELEASE_REVIEW"
    else:
        decision = "PASS_ROE3_CLAIM_BOUNDARY"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "issues": issues,
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "public_private_alignment_decision": alignment["decision"],
        "alignment_finding_count": alignment["finding_count"],
        "external_actions_performed": False,
        "workflow_enabled": False,
        "network_used": False,
        "token_printed": False,
        "private_kernel_exposed": False,
    }
    if write_result:
        _write_json(AUDIT_PATH, result)
    return result


def main() -> None:
    result = run_portfolio_release_audit()
    print(f"residualops_portfolio_release_audit: {result['decision']} risky_phrase_count={result['risky_phrase_count']}")


if __name__ == "__main__":
    main()
