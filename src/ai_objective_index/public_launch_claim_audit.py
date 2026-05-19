from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .public_launch_gate import OUTPUT_DIR
from .realdata_claim_audit import NEGATING_CONTEXT


OUTPUT_PATH = OUTPUT_DIR / "PUBLIC_LAUNCH_CLAIM_AUDIT_RESULT.json"

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
    "deploys production tools",
]

SCAN_TARGETS = [
    "README.md",
    "docs/community_launch.md",
    "docs/public_beta_release_plan.md",
    "docs/huggingface_demo.md",
    "public_launch",
    "release/public_beta_v0_2",
    "launch/manual_public_beta_v0_2",
    "hf_upload/space/README.md",
    "hf_upload/dataset/README.md",
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
    window = " ".join(lines[max(0, index - 10) : index + 5]).lower()
    return any(token in window for token in NEGATING_CONTEXT)


def audit_text(text: str, file_label: str = "<memory>") -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    contextual_mentions: list[dict[str, Any]] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        lowered = line.lower()
        for phrase in RISKY_PHRASES:
            if phrase not in lowered:
                continue
            item = {"file": file_label, "line": index + 1, "phrase": phrase, "text": line.strip()}
            if _is_negated(lines, index):
                contextual_mentions.append({**item, "counted": False})
            else:
                findings.append({**item, "counted": True})
    return {"findings": findings, "contextual_mentions": contextual_mentions}


def run_public_launch_claim_audit(
    files: list[str | Path] | None = None,
    write_result: bool = True,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    contextual_mentions: list[dict[str, Any]] = []
    scanned_files: list[str] = []
    for path in _iter_files(files):
        rel = str(path.relative_to(_repo_root())) if _repo_root() in path.parents else str(path)
        scanned_files.append(rel)
        result = audit_text(path.read_text(encoding="utf-8", errors="ignore"), rel)
        findings.extend(result["findings"])
        contextual_mentions.extend(result["contextual_mentions"])

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": "PASS" if not findings else "HOLD",
        "risky_phrase_count": len(findings),
        "findings": findings,
        "contextual_mentions": contextual_mentions,
        "scanned_files": scanned_files,
        "suggested_rewrites": [
            "Use: source-traced registry metadata candidates.",
            "Use: not verified, not security certified, not a quality guarantee.",
            "Use: read-only benchmark/demo, no purchasing advice or external actions.",
        ],
        "read_only": True,
        "live_network_used": False,
        "actual_publish_performed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_public_launch_claim_audit()
    print(
        "public_launch_claim_audit: "
        f"{result['overall_token']} "
        f"risky_phrase_count={result['risky_phrase_count']}"
    )


if __name__ == "__main__":
    main()
