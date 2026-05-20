from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OUTPUT_PATH = Path("public_launch") / "wave5" / "OBJECTIVE_ROUTER_CLAIM_BOUNDARY_AUDIT.json"
BLOCKED_PHRASES = [
    "verified capability",
    "safe tool",
    "security certified",
    "quality guaranteed",
    "best official tool",
    "production-ready",
    "all agents should use",
    "automatic security gateway",
    "purchasing recommendation",
    "legal advice",
]
ALLOWED_CONTEXT = [
    "not ",
    "must not",
    "do not",
    "does not",
    "not asserted",
    "forbidden",
    "blocked positive claims",
    "must_not_claim",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _allowed(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in ALLOWED_CONTEXT)


def _scan_file(path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line_no, line in enumerate(lines, start=1):
        lowered = line.lower()
        nearby = "\n".join(lines[max(0, line_no - 12) : min(len(lines), line_no + 2)]).lower()
        for phrase in BLOCKED_PHRASES:
            if phrase in lowered and not _allowed(line) and "not:" not in nearby and "must_not_claim" not in nearby:
                findings.append(
                    {
                        "file": str(path.relative_to(_repo_root())),
                        "line": line_no,
                        "phrase": phrase,
                        "text": line[:240],
                    }
                )
    return findings


def run_objective_router_claim_audit(write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    paths = [
        root / "README.md",
        root / "CHANGELOG.md",
    ]
    paths.extend(sorted((root / "docs" / "vnext").glob("objective_router*.md")))
    paths.extend(
        path
        for path in sorted((root / "public_launch" / "wave5").glob("*.json"))
        if path.name != OUTPUT_PATH.name
    )
    paths.extend(sorted((root / "public_launch" / "wave5").glob("*.md")))
    findings: list[dict[str, Any]] = []
    scanned: list[str] = []
    for path in paths:
        if path.exists() and path.is_file():
            scanned.append(str(path.relative_to(root)))
            findings.extend(_scan_file(path))
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": "PASS" if not findings else "BLOCK",
        "risky_phrase_count": len(findings),
        "findings": findings,
        "scanned_files": scanned,
        "allowed_wording": [
            "source-traced candidate",
            "route decision",
            "trust estimate",
            "evidence summary",
            "risk boundary",
            "missing fields",
            "known limits",
            "not verified",
            "security not assessed",
        ],
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }
    if write_result:
        destination = root / OUTPUT_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    result = run_objective_router_claim_audit()
    print(
        "vnext_objective_router_audit: "
        f"{result['overall_token']} risky_phrase_count={result['risky_phrase_count']} "
        "pypi_upload_performed=False mcp_registry_submission_performed=False"
    )


if __name__ == "__main__":
    main()
