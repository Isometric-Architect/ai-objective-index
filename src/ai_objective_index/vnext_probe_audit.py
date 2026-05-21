from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


OUTPUT_PATH = Path("public_launch") / "wave7" / "PROBE_CLAIM_BOUNDARY_AUDIT.json"
RISKY_PHRASES = [
    "probe verified",
    "safe tool",
    "security certified",
    "quality guaranteed",
    "production ready",
    "action authorized",
    "purchase recommended",
    "external validation",
    "live security scanner",
    "gateway protection",
]
ALLOW_CONTEXT = [
    "not ",
    "not verified",
    "are not",
    "they are not",
    "not action",
    "no ",
    "without ",
    "cannot ",
    "cannot verify",
    "cannot certify",
    "cannot guarantee",
    "must not ",
    "do not ",
    "does not ",
    "forbidden ",
    "forbidden_claims",
    "blocked ",
    "risky positive claims",
    "allowed:",
    "limitations",
    "claim boundary",
    "claim that",
    "claim_ceiling",
    "must_not_claim",
    "certify security",
    "guarantee quality",
]


def _is_allowed_context(text: str, start: int) -> bool:
    context = text[max(0, start - 120) : start + 120].lower()
    return any(marker in context for marker in ALLOW_CONTEXT)


def _scan_file(path: Path) -> list[dict[str, Any]]:
    try:
        raw_text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    if path.suffix == ".json":
        try:
            payload = json.loads(raw_text)
            _strip_allowed_json_fields(payload)
            raw_text = json.dumps(payload, ensure_ascii=False)
        except Exception:
            pass
    text = raw_text.lower()
    findings = []
    for phrase in RISKY_PHRASES:
        pattern = re.compile(rf"(?<![a-z0-9_-]){re.escape(phrase)}(?![a-z0-9_-])")
        for match in pattern.finditer(text):
            if _is_allowed_context(text, match.start()):
                continue
            findings.append({"path": str(path), "phrase": phrase, "position": match.start()})
    return findings


def _strip_allowed_json_fields(value: Any, key: str | None = None) -> None:
    if isinstance(value, dict):
        for item_key in list(value):
            if item_key in {"forbidden_claims", "must_not_claim", "claim_boundary", "claim_ceiling", "final_claim_ceiling"}:
                value[item_key] = "[CLAIM_BOUNDARY_TERMS_REDACTED_FOR_AUDIT]"
            else:
                _strip_allowed_json_fields(value[item_key], item_key)
    elif isinstance(value, list):
        for item in value:
            _strip_allowed_json_fields(item, key)


def run_probe_claim_audit(write_result: bool = True) -> dict[str, Any]:
    root = Path.cwd()
    paths: list[Path] = []
    paths.extend(sorted((root / "docs" / "vnext").glob("probe*.md")))
    paths.extend(sorted((root / "docs" / "vnext").glob("package_9e*.md")))
    wave7 = root / "public_launch" / "wave7"
    if wave7.exists():
        paths.extend(path for path in sorted(wave7.glob("*")) if path.name != OUTPUT_PATH.name)
    for path in [root / "README.md", root / "CHANGELOG.md"]:
        if path.exists():
            paths.append(path)
    findings = []
    for path in paths:
        if path.is_file():
            findings.extend(_scan_file(path))
    result = {
        "schema": "AOI_ProbeClaimBoundaryAudit/v0.1",
        "overall_token": "PASS" if not findings else "BLOCK",
        "risky_phrase_count": len(findings),
        "findings": findings,
        "scanned_files": [str(path) for path in paths if path.is_file()],
        "claim_boundary": [
            "local probe pass is not verification",
            "not security certified",
            "not a quality guarantee",
            "no action authorization",
            "no live MCP call or external tool execution",
        ],
        "pypi_upload_performed": False,
        "mcp_registry_submission_performed": False,
        "community_post_performed": False,
        "token_printed": False,
    }
    if write_result:
        (root / OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
        (root / OUTPUT_PATH).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    result = run_probe_claim_audit()
    print(
        "vnext_probe_audit: "
        f"{result['overall_token']} risky_phrase_count={result['risky_phrase_count']}"
    )


if __name__ == "__main__":
    main()
