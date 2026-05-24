from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root


OUTPUT_PATH = Path("public_launch") / "qira1" / "QIRA_CLAIM_BOUNDARY_AUDIT.json"
QIRA2_OUTPUT_PATH = Path("public_launch") / "qira2" / "QIRA_CLAIM_BOUNDARY_AUDIT.json"
QIRA3_OUTPUT_PATH = Path("public_launch") / "qira3" / "QIRA_CLAIM_BOUNDARY_AUDIT.json"
QIRA4_OUTPUT_PATH = Path("public_launch") / "qira4" / "QIRA_CLAIM_BOUNDARY_AUDIT.json"
QIRA5_OUTPUT_PATH = Path("public_launch") / "qira5" / "QIRA_CLAIM_BOUNDARY_AUDIT.json"
SCAN_PATHS = [
    Path("docs") / "qira_code_releasegate_plan.md",
    Path("docs") / "qira_releasegate_mvp.md",
    Path("docs") / "qira2_task_packet_intake.md",
    Path("docs") / "qira_local_packet_cli.md",
    Path("docs") / "qira3_patch_classification.md",
    Path("docs") / "qira_test_command_contract.md",
    Path("docs") / "qira4_github_action_dry_run.md",
    Path("docs") / "qira_github_action_limitations.md",
    Path("docs") / "qira5_pr_packet_generator.md",
    Path("docs") / "qira_pr_diff_packet_limitations.md",
    Path("docs") / "qira_action_license.md",
    Path("docs") / "qira_claim_boundaries.md",
    Path("public_launch") / "qira1",
    Path("public_launch") / "qira2",
    Path("public_launch") / "qira3",
    Path("public_launch") / "qira4",
    Path("public_launch") / "qira5",
]

RISKY_PATTERNS = [
    re.compile(r"\bverified\s+patch\b", re.I),
    re.compile(r"\bsafe\s+patch\b", re.I),
    re.compile(r"\bsecurity\s+certified\b", re.I),
    re.compile(r"\bquality\s+guaranteed\b", re.I),
    re.compile(r"\bproduction[- ]ready\b", re.I),
    re.compile(r"\bdeployment\s+approved\b", re.I),
    re.compile(r"\blegal\s+compliance\s+confirmed\b", re.I),
    re.compile(r"\bexternal\s+action\s+authorized\b", re.I),
]

SAFE_CONTEXT = [
    "not ",
    "must not",
    "does not",
    "do not",
    "without claiming",
    "claim boundary",
    "must_not_claim",
]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _iter_files() -> list[Path]:
    root = _repo_root()
    files: list[Path] = []
    for relative in SCAN_PATHS:
        path = root / relative
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".py", ".txt"}:
            if path != root / OUTPUT_PATH:
                files.append(path)
        elif path.is_dir():
            files.extend(
                child
                for child in path.rglob("*")
                if child.is_file() and child.suffix.lower() in {".md", ".json", ".txt"} and child != root / OUTPUT_PATH
            )
    return sorted(set(files))


def _safe_line(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in SAFE_CONTEXT)


def run_qira_claim_audit(write_result: bool = True) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for path in _iter_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = str(path.relative_to(_repo_root())).replace("\\", "/")
        for index, line in enumerate(text.splitlines(), start=1):
            if _safe_line(line):
                continue
            for pattern in RISKY_PATTERNS:
                if pattern.search(line):
                    findings.append({"path": rel, "line": index, "pattern": pattern.pattern})
    decision = "BLOCK_QIRA_OVERCLAIM" if findings else "PASS_QIRA_CLAIM_BOUNDARY"
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "risky_phrase_count": len(findings),
        "findings": findings[:100],
        "allowed_language": [
            "behavior contract",
            "residual ledger",
            "patch receipt",
            "action license",
            "ALLOW/HOLD/BLOCK",
            "local release-gate receipt",
        ],
        "must_not_claim": [
            "do not claim verified patch status",
            "do not claim safety",
            "do not claim security certification",
            "do not claim quality guarantee",
            "do not claim production readiness",
            "do not claim deployment approval",
            "do not claim external action authorization",
        ],
        "external_actions_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
        _write_json(QIRA2_OUTPUT_PATH, result)
        _write_json(QIRA3_OUTPUT_PATH, result)
        _write_json(QIRA4_OUTPUT_PATH, result)
        _write_json(QIRA5_OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_qira_claim_audit()
    print(f"qira_claim_audit: {result['decision']} risky_phrase_count={result['risky_phrase_count']}")


if __name__ == "__main__":
    main()
