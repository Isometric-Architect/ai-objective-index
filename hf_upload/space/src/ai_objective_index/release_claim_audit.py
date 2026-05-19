from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_PATH = Path("data/generated/release_claim_audit_v0_1.json")

PUBLIC_FILES = [
    "README.md",
    "docs/community_launch.md",
    "docs/launch_notes.md",
    "docs/public_claim_policy.md",
]

RISKY_PHRASES = [
    "all ai will use",
    "official standard",
    "guaranteed quality",
    "guarantees quality",
    "legal advice",
    "financial advice",
    "medical advice",
    "purchasing advice",
    "certified safe",
    "security certified",
    "automatically buys",
    "books appointments",
    "sends email",
    "logs in",
    "signs contracts",
]

NEGATING_CONTEXT = [
    "forbidden",
    "not ",
    "not a",
    "not an",
    "does not",
    "do not",
    "no ",
    "never",
    "must not",
    "blocked",
    "without",
    "is not",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _candidate_files() -> list[Path]:
    root = _repo_root()
    files = [root / path for path in PUBLIC_FILES]
    release_dir = root / "release" / "public_beta_v0_1"
    if release_dir.exists():
        files.extend(sorted(release_dir.glob("*.md")))
    return [path for path in files if path.exists()]


def _is_negated(lines: list[str], index: int) -> bool:
    window = " ".join(lines[max(0, index - 8) : index + 4]).lower()
    return any(token in window for token in NEGATING_CONTEXT)


def run_release_claim_audit() -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    contextual_mentions: list[dict[str, Any]] = []
    for path in _candidate_files():
        rel = str(path.relative_to(_repo_root()))
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for index, line in enumerate(lines):
            lowered = line.lower()
            for phrase in RISKY_PHRASES:
                if phrase not in lowered:
                    continue
                item = {
                    "file": rel,
                    "line": index + 1,
                    "phrase": phrase,
                    "text": line.strip(),
                }
                if _is_negated(lines, index):
                    contextual_mentions.append({**item, "counted": False})
                else:
                    findings.append({**item, "counted": True})

    suggested_rewrites = [
        "Use: AOI is an experimental read-only MCP/API benchmark tool.",
        "Use: AOI outputs are not quality guarantees or purchasing advice.",
        "Use: Manual publishing and registry submission are not performed by this repository.",
    ]
    risky_phrase_count = len(findings)
    overall = "PASS" if risky_phrase_count == 0 else "HOLD"
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "risky_phrase_count": risky_phrase_count,
        "findings": findings,
        "contextual_mentions": contextual_mentions,
        "overall_token": overall,
        "suggested_rewrites": suggested_rewrites,
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }


def save_release_claim_audit(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    payload = results or run_release_claim_audit()
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    results = run_release_claim_audit()
    path = save_release_claim_audit(results)
    print(f"Saved release claim audit: {path}")
    print(f"claim_audit={results['overall_token']} risky_phrase_count={results['risky_phrase_count']}")


if __name__ == "__main__":
    main()
