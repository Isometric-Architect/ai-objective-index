from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_PATH = Path("data/generated/realdata_claim_audit_v0_2.json")

PUBLIC_FILES = [
    "README.md",
    "docs/community_launch.md",
    "docs/public_beta_release_plan.md",
    "docs/mcp_registry_intake.md",
    "docs/public_data_intake_policy.md",
    "docs/manual_publish_checklist.md",
    "hf_dataset/README.md",
    "hf_demo/README.md",
]

RISKY_PHRASES = [
    "verified mcp servers",
    "safe mcp servers",
    "security certified",
    "quality guaranteed",
    "official best ranking",
    "production-ready",
    "purchasing advice",
    "legal advice",
    "all ai will use",
    "official standard",
    "automatically buys",
    "signs contracts",
    "sends email",
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
    "are not",
    "known limits",
    "limit",
    "limitations",
    "boundary",
    "claim boundary",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _candidate_files() -> list[Path]:
    root = _repo_root()
    files = [root / path for path in PUBLIC_FILES]
    release_dir = root / "release" / "public_beta_v0_2"
    if release_dir.exists():
        files.extend(sorted(release_dir.glob("*.md")))
    return [path for path in files if path.exists()]


def _is_negated(lines: list[str], index: int) -> bool:
    window = " ".join(lines[max(0, index - 10) : index + 5]).lower()
    return any(token in window for token in NEGATING_CONTEXT)


def audit_text(text: str, file_label: str = "<memory>") -> dict[str, Any]:
    """Audit text for real-data public beta overclaims.

    This helper is intentionally simple and deterministic so tests can probe
    positive and forbidden-context examples without network or LLM calls.
    """

    findings: list[dict[str, Any]] = []
    contextual_mentions: list[dict[str, Any]] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        lowered = line.lower()
        for phrase in RISKY_PHRASES:
            if phrase not in lowered:
                continue
            item = {
                "file": file_label,
                "line": index + 1,
                "phrase": phrase,
                "text": line.strip(),
            }
            if _is_negated(lines, index):
                contextual_mentions.append({**item, "counted": False})
            else:
                findings.append({**item, "counted": True})
    return {"findings": findings, "contextual_mentions": contextual_mentions}


def run_realdata_claim_audit(files: list[Path] | None = None) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    contextual_mentions: list[dict[str, Any]] = []
    for path in files or _candidate_files():
        rel = str(path.relative_to(_repo_root())) if path.is_absolute() and _repo_root() in path.parents else str(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        result = audit_text(text, rel)
        findings.extend(result["findings"])
        contextual_mentions.extend(result["contextual_mentions"])

    suggested_rewrites = [
        "Use: public_beta_mcp contains Official MCP Registry metadata candidates.",
        "Use: candidates are not verified, security certified, quality guaranteed, or action-ready.",
        "Use: AOI is read-only and does not buy, book, log in, send email, purchase, or sign contracts.",
    ]
    risky_phrase_count = len(findings)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "risky_phrase_count": risky_phrase_count,
        "findings": findings,
        "contextual_mentions": contextual_mentions,
        "overall_token": "PASS" if risky_phrase_count == 0 else "HOLD",
        "suggested_rewrites": suggested_rewrites,
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }


def save_realdata_claim_audit(
    results: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    payload = results or run_realdata_claim_audit()
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def main() -> None:
    results = run_realdata_claim_audit()
    path = save_realdata_claim_audit(results)
    print(f"Saved real-data claim audit: {path}")
    print(
        "realdata_claim_audit: "
        f"{results['overall_token']} "
        f"risky_phrase_count={results['risky_phrase_count']} "
        "live_network_used=False"
    )


if __name__ == "__main__":
    main()
