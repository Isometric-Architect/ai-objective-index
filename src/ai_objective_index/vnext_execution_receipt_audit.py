from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


OUTPUT_PATH = Path("public_launch") / "wave6" / "EXECUTION_RECEIPT_CLAIM_BOUNDARY_AUDIT.json"
BLOCKED_PHRASES = [
    "verified by receipt",
    "safe tool",
    "security certified",
    "quality guaranteed",
    "production ready",
    "action authorized",
    "purchase recommended",
    "legal advice",
    "external validation",
]
ALLOWED_CONTEXT = [
    "not ",
    "must not",
    "do not",
    "does not",
    "cannot",
    "no action authorization",
    "not verified",
    "not security certified",
    "blocked positive claims",
    "forbidden",
    "risk phrase",
    "must_not_claim",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _allowed(lines: list[str], index: int) -> bool:
    context = "\n".join(lines[max(0, index - 6) : min(len(lines), index + 3)]).lower()
    return any(marker in context for marker in ALLOWED_CONTEXT)


def _scan_file(path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    root = _repo_root()
    for idx, line in enumerate(lines):
        lowered = line.lower()
        for phrase in BLOCKED_PHRASES:
            if phrase in lowered and not _allowed(lines, idx):
                findings.append(
                    {
                        "file": str(path.relative_to(root)),
                        "line": idx + 1,
                        "phrase": phrase,
                        "text": line[:240],
                    }
                )
    return findings


def run_execution_receipt_claim_audit(write_result: bool = True) -> dict[str, Any]:
    root = _repo_root()
    scan_paths: list[Path] = []
    scan_paths.extend(sorted((root / "docs" / "vnext").glob("execution_receipt*.md")))
    receipt_overlay = root / "docs" / "vnext" / "receipt_route_overlay.md"
    if receipt_overlay.exists():
        scan_paths.append(receipt_overlay)
    wave6 = root / "public_launch" / "wave6"
    if wave6.exists():
        scan_paths.extend(
            sorted(
                path
                for path in wave6.iterdir()
                if path.suffix in {".json", ".md"} and path.name != OUTPUT_PATH.name
            )
        )
    for path in [root / "README.md", root / "CHANGELOG.md"]:
        if path.exists():
            scan_paths.append(path)

    findings: list[dict[str, Any]] = []
    scanned: list[str] = []
    for path in scan_paths:
        if not path.is_file():
            continue
        scanned.append(str(path.relative_to(root)))
        findings.extend(_scan_file(path))
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": "PASS" if not findings else "BLOCK",
        "risky_phrase_count": len(findings),
        "findings": findings,
        "scanned_files": sorted(set(scanned)),
        "allowed_wording": [
            "receipt memory",
            "self-reported outcome",
            "known failure",
            "residual note",
            "local fixture",
            "not verified",
            "not security certified",
            "no action authorization",
        ],
        "blocked_positive_claims": BLOCKED_PHRASES,
        "external_execution": False,
        "probe_execution": False,
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
    result = run_execution_receipt_claim_audit()
    print(
        "vnext_execution_receipt_audit: "
        f"{result['overall_token']} risky_phrase_count={result['risky_phrase_count']} "
        "external_execution=False"
    )


if __name__ == "__main__":
    main()
