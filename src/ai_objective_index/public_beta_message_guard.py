from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .public_launch_gate import OUTPUT_DIR
from .realdata_claim_audit import NEGATING_CONTEXT


OUTPUT_PATH = OUTPUT_DIR / "PUBLIC_BETA_MESSAGE_GUARD_RESULT.json"

ALLOWED_PHRASES = [
    "read-only",
    "source-traced",
    "objective-based ranking",
    "registry metadata candidates",
    "please test",
    "break it",
    "not verified",
    "not security certified",
    "not quality guarantee",
    "not a quality guarantee",
]

BLOCKED_POSITIVE_CLAIMS = [
    "ai google",
    "best mcp servers",
    "verified servers",
    "safe servers",
    "production-ready",
    "official standard",
    "all ai will use",
    "guaranteed ranking",
]

SCAN_TARGETS = [
    "public_launch/PUBLIC_BETA_POST_DRAFT_NO_CONTACT.md",
    "public_launch/PUBLIC_ANNOUNCEMENT_DRAFTS.md",
    "docs/community_launch.md",
    "launch/manual_public_beta_v0_2/COMMUNITY_POST_DRAFTS.md",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _iter_files(targets: list[str | Path] | None = None) -> list[Path]:
    root = _repo_root()
    files: list[Path] = []
    for item in targets or SCAN_TARGETS:
        path = Path(item)
        if not path.is_absolute():
            path = root / path
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(child for child in path.rglob("*.md") if child.is_file())
    return sorted(set(files))


def _is_negated(lines: list[str], index: int) -> bool:
    window = " ".join(lines[max(0, index - 5) : index + 5]).lower()
    return any(token in window for token in NEGATING_CONTEXT)


def audit_message_text(text: str, file_label: str = "<memory>") -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    allowed_mentions: list[dict[str, Any]] = []
    contextual_mentions: list[dict[str, Any]] = []
    lines = text.splitlines()
    lowered_text = text.lower()
    for phrase in ALLOWED_PHRASES:
        if phrase in lowered_text:
            allowed_mentions.append({"file": file_label, "phrase": phrase})
    for index, line in enumerate(lines):
        lowered = line.lower()
        for phrase in BLOCKED_POSITIVE_CLAIMS:
            if phrase not in lowered:
                continue
            item = {"file": file_label, "line": index + 1, "phrase": phrase, "text": line.strip()}
            if _is_negated(lines, index):
                contextual_mentions.append({**item, "counted": False})
            else:
                findings.append({**item, "counted": True})
    return {
        "findings": findings,
        "allowed_mentions": allowed_mentions,
        "contextual_mentions": contextual_mentions,
    }


def run_public_beta_message_guard(
    files: list[str | Path] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    allowed_mentions: list[dict[str, Any]] = []
    contextual_mentions: list[dict[str, Any]] = []
    scanned_files: list[str] = []
    for path in _iter_files(files):
        rel = str(path.relative_to(_repo_root())) if _repo_root() in path.parents else str(path)
        scanned_files.append(rel)
        result = audit_message_text(path.read_text(encoding="utf-8", errors="ignore"), rel)
        findings.extend(result["findings"])
        allowed_mentions.extend(result["allowed_mentions"])
        contextual_mentions.extend(result["contextual_mentions"])
    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": "PASS" if not findings else "HOLD",
        "risky_phrase_count": len(findings),
        "findings": findings,
        "allowed_mentions": allowed_mentions,
        "contextual_mentions": contextual_mentions,
        "scanned_files": scanned_files,
        "blocked_positive_claims": BLOCKED_POSITIVE_CLAIMS,
        "allowed_phrases": ALLOWED_PHRASES,
        "suggested_rewrites": [
            "Use: read-only source-traced objective-based ranking.",
            "Use: registry metadata candidates, not verified or security certified.",
            "Use: please test/break it and open issues.",
        ],
        "actual_post_performed": False,
        "public_switch_performed": False,
        "live_network_used": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_public_beta_message_guard()
    print(
        "public_beta_message_guard: "
        f"{result['overall_token']} "
        f"risky_phrase_count={result['risky_phrase_count']} "
        "actual_post_performed=False"
    )


if __name__ == "__main__":
    main()
