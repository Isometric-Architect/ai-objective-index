from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


WAVE3_DIR = Path("public_launch") / "wave3"
AUDIT_PATH = WAVE3_DIR / "VNEXT_CLAIM_BOUNDARY_AUDIT.json"
ALIGNMENT_PATH = WAVE3_DIR / "VNEXT_ALIGNMENT_RESULT.json"
ROADMAP_PATH = WAVE3_DIR / "VNEXT_ROADMAP.md"
HOLD_NOTE_PATH = WAVE3_DIR / "VNEXT_PACKAGE_HOLD_NOTE.md"

BLOCKED_POSITIVE_CLAIMS = [
    "already a security gateway",
    "verified capabilities",
    "verified mcp servers",
    "security certified",
    "quality guaranteed",
    "official standard",
    "dominates the ecosystem",
    "all agents will use",
]

ALLOWED_CONTEXT_HINTS = [
    "do not claim",
    "does not claim",
    "not ",
    "roadmap",
    "strategy",
    "schema",
    "future",
    "not already",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write(path: Path, text: str) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return destination


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    return _write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def _iter_vnext_docs() -> list[Path]:
    root = _repo_root() / "docs" / "vnext"
    if not root.exists():
        return []
    return sorted(path for path in root.glob("*.md") if path.is_file())


def _is_allowed_context(line: str) -> bool:
    lowered = line.lower()
    return any(hint in lowered for hint in ALLOWED_CONTEXT_HINTS)


def run_vnext_claim_audit(write_result: bool = True) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    scanned_files: list[str] = []
    for path in _iter_vnext_docs():
        rel = str(path.relative_to(_repo_root()))
        scanned_files.append(rel)
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            lowered = line.lower()
            for phrase in BLOCKED_POSITIVE_CLAIMS:
                if phrase in lowered and not _is_allowed_context(line):
                    findings.append({"file": rel, "line": line_no, "phrase": phrase, "text": line[:240]})

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": "PASS" if not findings else "BLOCK",
        "findings": findings,
        "risky_phrase_count": len(findings),
        "scanned_files": scanned_files,
        "vnext_positioning": "AI Agent Capability Trust Router",
        "pypi_upload_performed": False,
        "testpypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(AUDIT_PATH, result)
        alignment = {
            "generated_at": result["generated_at"],
            "overall_token": result["overall_token"],
            "positioning": "AI Agent Capability Trust Router",
            "v0_2_status": "public beta engine remains active",
            "vnext_status": "strategy_schema_alignment",
            "first_vertical": "Coding Agent Tool Selection",
            "pypi_upload_paused": True,
            "mcp_registry_submission_paused": True,
            "not_asserted": [
                "security certification",
                "quality guarantee",
                "capability verification",
                "purchasing advice",
                "security gateway already implemented",
            ],
        }
        _write_json(ALIGNMENT_PATH, alignment)
        _write(
            ROADMAP_PATH,
            """# AOI vNext Roadmap

1. Package 9A: strategy, schema, and claim-boundary alignment.
2. Package 9B: Capability Trust Schema MVP.
3. Package 9C: read-only probe-result ingestion and receipt loop.
4. Package 9D: coding-agent tool selection vertical.
5. Resume PyPI/MCP Registry path only after vNext positioning and schemas are stable.

No upload, submission, or community post is performed by Package 9A.
""",
        )
        _write(
            HOLD_NOTE_PATH,
            """# vNext Package Hold Note

PyPI upload and MCP Registry submission are paused until Package 9A alignment passes.

This is not a blocker. It is a positioning and safety alignment step so AOI can move from a public beta ranking engine toward an AI Agent Capability Trust Router without overclaiming.

Current claim boundary remains: source-traced capability candidates, objective-relative routing, ALLOW/HOLD/BLOCK, not verified, not security certified, not a quality guarantee, no purchasing advice, and no payment/booking/login/email/purchase/contract actions.
""",
        )
    return result


def main() -> None:
    result = run_vnext_claim_audit()
    print(
        "vnext_claim_audit: "
        f"{result['overall_token']} "
        f"risky_phrase_count={result['risky_phrase_count']} "
        "pypi_upload_performed=False mcp_registry_submission_performed=False"
    )


if __name__ == "__main__":
    main()
