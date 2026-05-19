from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .realdata_claim_audit import RISKY_PHRASES, audit_text


DEFAULT_OUTPUT_PATH = Path("data/generated/launch_claim_guard_result_v0_2.json")

LAUNCH_FILES = [
    "launch/manual_public_beta_v0_2/README_LAUNCH_STEPS.md",
    "launch/manual_public_beta_v0_2/GITHUB_RELEASE_DRAFT.md",
    "launch/manual_public_beta_v0_2/HUGGINGFACE_SPACE_UPLOAD_GUIDE.md",
    "launch/manual_public_beta_v0_2/HUGGINGFACE_DATASET_UPLOAD_GUIDE.md",
    "launch/manual_public_beta_v0_2/COMMUNITY_POST_DRAFTS.md",
    "launch/manual_public_beta_v0_2/MCP_REGISTRY_SUBMISSION_DRAFT.md",
    "launch/manual_public_beta_v0_2/FINAL_SAFETY_CHECKLIST.md",
    "launch/manual_public_beta_v0_2/FINAL_CLAIM_BOUNDARY.md",
    "launch/manual_public_beta_v0_2/FINAL_KNOWN_LIMITS.md",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _candidate_files(files: list[str | Path] | None = None) -> list[Path]:
    root = _repo_root()
    candidates = []
    for item in files or LAUNCH_FILES:
        path = Path(item)
        if not path.is_absolute():
            path = root / path
        if path.exists():
            candidates.append(path)
    return candidates


def run_launch_claim_guard(files: list[str | Path] | None = None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    contextual_mentions: list[dict[str, Any]] = []
    for path in _candidate_files(files):
        rel = str(path.relative_to(_repo_root())) if _repo_root() in path.parents else str(path)
        result = audit_text(path.read_text(encoding="utf-8", errors="ignore"), rel)
        findings.extend(result["findings"])
        contextual_mentions.extend(result["contextual_mentions"])
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": "PASS" if not findings else "HOLD",
        "risky_phrase_count": len(findings),
        "findings": findings,
        "contextual_mentions": contextual_mentions,
        "suggested_rewrites": [
            "Use: source-traced registry metadata candidates, not verified MCP servers.",
            "Use: read-only benchmark, not security certification or quality guarantee.",
            "Use: manual publish only; no automatic external actions.",
        ],
        "risky_phrases": RISKY_PHRASES,
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }


def save_launch_claim_guard(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    payload = results or run_launch_claim_guard()
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    results = run_launch_claim_guard()
    path = save_launch_claim_guard(results)
    print(f"Saved launch claim guard: {path}")
    print(
        "launch_claim_guard: "
        f"{results['overall_token']} "
        f"risky_phrase_count={results['risky_phrase_count']} "
        "live_network_used=False"
    )


if __name__ == "__main__":
    main()
