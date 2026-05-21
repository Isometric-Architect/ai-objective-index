from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .no_secrets_audit import scan_text_for_secrets


OUTPUT_PATH = Path("data/generated/hf_upload_audit_result_v0_2.json")
UPLOAD_ROOT = Path("hf_upload")
TEXT_SUFFIXES = {".md", ".py", ".txt", ".json", ".jsonl", ".toml", ".yaml", ".yml"}
BLOCKED_PARTS = {".git", ".pytest_cache", "__pycache__"}
NETWORK_SNIPPETS = ["requests.get", "urllib.request", "urlopen(", "httpx.get", "fetch("]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _exists(rel: str) -> bool:
    return (_repo_root() / rel).exists()


def _line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip())


def _iter_upload_files() -> list[Path]:
    root = _repo_root() / UPLOAD_ROOT
    if not root.exists():
        return []
    return [path for path in root.rglob("*") if path.is_file()]


def run_hf_upload_audit() -> dict[str, Any]:
    root = _repo_root()
    files = _iter_upload_files()
    required_files = [
        "hf_upload/space/app.py",
        "hf_upload/space/requirements.txt",
        "hf_upload/space/README.md",
        "hf_upload/dataset/README.md",
        "hf_upload/dataset/mcp_registry_beta_candidates.jsonl",
        "hf_upload/dataset/mcp_registry_source_traces.jsonl",
        "hf_upload/dataset/public_beta_mcp_dataset.json",
    ]
    missing = [rel for rel in required_files if not _exists(rel)]
    blocked_files = [
        str(path.relative_to(root))
        for path in files
        if any(part in BLOCKED_PARTS for part in path.parts) or path.name.startswith(".env")
    ]

    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = str(path.relative_to(root))
        result = scan_text_for_secrets(text, rel)
        for finding in result["findings"]:
            finding_text = finding.get("text", "")
            if "re.compile" in finding_text and "PRIVATE KEY" in finding_text:
                warnings.append({**finding, "severity": "warning", "pattern_definition": True})
            else:
                findings.append(finding)
        warnings.extend(result["warnings"])

    app_text = (root / "hf_upload/space/app.py").read_text(encoding="utf-8", errors="ignore") if _exists("hf_upload/space/app.py") else ""
    network_fetch_snippets = [snippet for snippet in NETWORK_SNIPPETS if snippet in app_text]

    boundary_text = "\n".join(
        [
            (root / "hf_upload/space/README.md").read_text(encoding="utf-8", errors="ignore") if _exists("hf_upload/space/README.md") else "",
            (root / "hf_upload/dataset/README.md").read_text(encoding="utf-8", errors="ignore") if _exists("hf_upload/dataset/README.md") else "",
        ]
    ).lower()
    claim_boundaries_present = all(
        phrase in boundary_text
        for phrase in ["not verified", "not security certified", "not a quality guarantee"]
    )
    jsonl_counts = {
        "action_objects.jsonl": _line_count(root / "hf_upload/dataset/action_objects.jsonl"),
        "source_traces.jsonl": _line_count(root / "hf_upload/dataset/source_traces.jsonl"),
        "mcp_registry_beta_candidates.jsonl": _line_count(root / "hf_upload/dataset/mcp_registry_beta_candidates.jsonl"),
        "mcp_registry_source_traces.jsonl": _line_count(root / "hf_upload/dataset/mcp_registry_source_traces.jsonl"),
    }
    line_count_ok = jsonl_counts["mcp_registry_beta_candidates.jsonl"] > 0 and jsonl_counts["mcp_registry_source_traces.jsonl"] > 0

    errors: list[str] = []
    if missing:
        errors.append("Required HF upload files are missing.")
    if blocked_files:
        errors.append("Blocked cache/env files are present in hf_upload.")
    if findings:
        errors.append("Secret-like findings are present.")
    if network_fetch_snippets:
        errors.append("Space app contains network-fetch snippets.")
    if not claim_boundaries_present:
        errors.append("README claim boundaries are incomplete.")
    if not line_count_ok:
        errors.append("Expected dataset JSONL files are empty.")

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "overall_token": "PASS" if not errors else "HOLD",
        "checks": {
            "required_files": {"pass": not missing, "missing": missing},
            "blocked_files": {"pass": not blocked_files, "files": blocked_files},
            "no_secrets": {"pass": not findings, "finding_count": len(findings), "warning_count": len(warnings)},
            "app_no_network_fetch": {"pass": not network_fetch_snippets, "snippets": network_fetch_snippets},
            "claim_boundaries": {"pass": claim_boundaries_present},
            "dataset_jsonl_counts": jsonl_counts,
        },
        "errors": errors,
        "warnings": warnings,
        "actual_upload_performed": False,
        "tokens_used": False,
        "live_network_used": False,
        "read_only": True,
    }
    destination = root / OUTPUT_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    result = run_hf_upload_audit()
    print(
        "hf_upload_audit: "
        f"{result['overall_token']} "
        f"errors={len(result['errors'])} "
        "actual_upload_performed=False"
    )


if __name__ == "__main__":
    main()
