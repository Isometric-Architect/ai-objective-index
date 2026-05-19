from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .deployment_link_sync import GITHUB_URL, HF_DATASET_URL, HF_SPACE_URL, OUTPUT_DIR
from .realdata_claim_audit import audit_text


OUTPUT_PATH = OUTPUT_DIR / "HF_GITHUB_CROSSLINK_AUDIT_RESULT.json"

DEFAULT_SCAN_TARGETS = [
    "README.md",
    "docs/huggingface_demo.md",
    "hf_upload/space/README.md",
    "hf_upload/dataset/README.md",
    "launch/manual_public_beta_v0_2",
    "release/public_beta_v0_2",
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
    for item in targets or DEFAULT_SCAN_TARGETS:
        path = Path(item)
        if not path.is_absolute():
            path = root / path
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(child for child in path.rglob("*.md") if child.is_file())
    return sorted(set(files))


def _private_context_ok(text: str, url: str) -> bool:
    lowered = text.lower()
    index = lowered.find(url.lower())
    if index < 0:
        return False
    window = lowered[max(0, index - 160) : index + 240]
    return any(marker in window for marker in ["private", "hold", "manual", "not public", "unless the owner manually"])


def _has_positive_public_claim(text: str) -> bool:
    lowered = text.lower()
    risky = [
        "public release is complete",
        "now publicly released",
        "verified mcp servers",
        "safe mcp servers",
        "security certified",
        "quality guaranteed",
    ]
    for phrase in risky:
        if phrase in lowered:
            index = lowered.find(phrase)
            window = lowered[max(0, index - 100) : index + 160]
            if not any(marker in window for marker in ["not ", "no ", "forbidden", "do not", "known limit", "not a"]):
                return True
    return False


def audit_crosslinks(
    files: list[str | Path] | None = None,
    github_url: str = GITHUB_URL,
    hf_space_url: str = HF_SPACE_URL,
    hf_dataset_url: str = HF_DATASET_URL,
    write_result: bool = True,
) -> dict[str, Any]:
    scanned_files: list[str] = []
    combined = ""
    findings: list[dict[str, Any]] = []
    contextual_mentions: list[dict[str, Any]] = []
    public_claim_findings: list[dict[str, Any]] = []

    for path in _iter_files(files):
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = str(path.relative_to(_repo_root())) if _repo_root() in path.parents else str(path)
        scanned_files.append(rel)
        combined += "\n" + text
        claim_result = audit_text(text, rel)
        findings.extend(claim_result["findings"])
        contextual_mentions.extend(claim_result["contextual_mentions"])
        if _has_positive_public_claim(text):
            public_claim_findings.append({"file": rel, "reason": "positive public/verified/safe claim detected"})

    github_present = github_url in combined
    hf_space_present = hf_space_url in combined
    hf_dataset_present = hf_dataset_url in combined
    private_wording_ok = all(
        [
            _private_context_ok(combined, github_url),
            _private_context_ok(combined, hf_space_url),
            _private_context_ok(combined, hf_dataset_url),
        ]
    )
    missing_links = [
        name
        for name, present in [
            ("github", github_present),
            ("hf_space", hf_space_present),
            ("hf_dataset", hf_dataset_present),
        ]
        if not present
    ]

    errors: list[str] = []
    if missing_links:
        errors.append(f"Missing deployment links: {', '.join(missing_links)}")
    if not private_wording_ok:
        errors.append("One or more deployment links lack nearby private/HOLD/manual wording.")
    if findings or public_claim_findings:
        errors.append("Forbidden or risky positive claim found in crosslink audit.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": "PASS" if not errors else "HOLD",
        "scanned_files": scanned_files,
        "github_url_present": github_present,
        "hf_space_url_present": hf_space_present,
        "hf_dataset_url_present": hf_dataset_present,
        "private_wording_ok": private_wording_ok,
        "missing_links": missing_links,
        "risky_phrase_count": len(findings) + len(public_claim_findings),
        "findings": findings + public_claim_findings,
        "contextual_mentions": contextual_mentions,
        "errors": errors,
        "public_release_claimed": False,
        "actual_publish_performed": False,
        "read_only": True,
        "live_network_used": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = audit_crosslinks()
    print(
        "hf_github_crosslink_audit: "
        f"{result['overall_token']} "
        f"missing_links={len(result['missing_links'])} "
        f"risky_phrase_count={result['risky_phrase_count']}"
    )


if __name__ == "__main__":
    main()
