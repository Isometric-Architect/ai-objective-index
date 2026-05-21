from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .real_pypi_upload_gate import _repo_root
from .tech_protection_audit import _git_ls_files, _safe_context


OUTPUT_PATH = Path("public_launch") / "wave12_tech_protection" / "PUBLIC_PRIVATE_SPLIT_AUDIT.json"

REQUIRED_DOC = Path("docs") / "public_private_split.md"
PRIVATE_DETAIL_PATTERNS = [
    re.compile(r"\bprovider trust prior\b\s*[:=]\s*[-0-9.]+", re.I),
    re.compile(r"\b(private|commercial)\s+(weight|threshold|calibration)\b\s*[:=]\s*[-0-9.]+", re.I),
    re.compile(r"\breceipt weighting logic\b\s*[:=]", re.I),
    re.compile(r"\bprivate probe seed\b\s*[:=]", re.I),
    re.compile(r"\banti-gaming rule\b\s*[:=]", re.I),
]


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    destination = _repo_root() / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def scan_text_for_private_split_violations(text: str, path: str = "<memory>") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for index, line in enumerate(text.splitlines(), start=1):
        if _safe_context(line):
            continue
        for pattern in PRIVATE_DETAIL_PATTERNS:
            if pattern.search(line):
                findings.append({"path": path, "line": index, "pattern": pattern.pattern})
    return findings


def run_public_private_split_audit(write_result: bool = True) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for relative in _git_ls_files():
        full = _repo_root() / relative
        if not full.exists() or full.is_dir() or full.suffix.lower() not in {".md", ".py", ".json", ".toml"} or full.stat().st_size > 1_500_000:
            continue
        try:
            text = full.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        findings.extend(scan_text_for_private_split_violations(text, relative.replace("\\", "/")))

    split_doc = _repo_root() / REQUIRED_DOC
    split_doc_text = split_doc.read_text(encoding="utf-8", errors="ignore") if split_doc.exists() else ""
    required_public_terms = ["schemas", "API/MCP", "high-level", "ALLOW/HOLD/BLOCK"]
    required_private_terms = ["weights", "thresholds", "anti-gaming", "provider trust priors", "private negative controls"]
    public_terms_present = all(term.lower() in split_doc_text.lower() for term in required_public_terms)
    private_terms_present = all(term.lower() in split_doc_text.lower() for term in required_private_terms)

    if findings:
        decision = "BLOCK_PRIVATE_DETAILS_PUBLIC"
    elif not split_doc.exists() or not public_terms_present or not private_terms_present:
        decision = "HOLD_SPLIT_DOCS_INCOMPLETE"
    else:
        decision = "PASS_PUBLIC_PRIVATE_SPLIT_CLEAR"

    result = {
        "generated_at": datetime.now(UTC).isoformat(),
        "decision": decision,
        "split_doc_exists": split_doc.exists(),
        "public_terms_present": public_terms_present,
        "private_terms_present": private_terms_present,
        "private_detail_findings": findings[:100],
        "finding_count": len(findings),
        "public_allowed": ["schemas", "endpoint shapes", "MCP tool descriptions", "high-level score components", "source-trace methodology", "ALLOW/HOLD/BLOCK labels", "limitations", "sample public_beta_mcp data"],
        "private_reserved": ["exact operational weights", "scoring thresholds", "anti-gaming heuristics", "private negative controls", "private probe seeds", "provider trust priors", "receipt weighting logic", "commercial routing policy", "private data acquisition strategy"],
        "mcp_registry_submission_performed": False,
        "token_printed": False,
    }
    if write_result:
        _write_json(OUTPUT_PATH, result)
    return result


def main() -> None:
    result = run_public_private_split_audit()
    print(f"public_private_split_audit: {result['decision']} findings={result['finding_count']}")


if __name__ == "__main__":
    main()
