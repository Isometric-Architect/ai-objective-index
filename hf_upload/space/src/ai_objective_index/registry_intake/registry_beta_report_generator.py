from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .registry_beta_dataset_builder import build_registry_beta_dataset
from .registry_quality_audit import run_registry_quality_audit, save_registry_quality_audit


DEFAULT_OUTPUT = Path("data/registry/mcp_registry_beta_report_v0_1.md")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def generate_registry_beta_report() -> str:
    gate = build_registry_beta_dataset()
    audit = run_registry_quality_audit()
    save_registry_quality_audit(audit)
    candidate_count = int(gate.get("beta_candidate_count", 0))
    candidates = [
        result
        for result in gate.get("object_results", [])
        if result.get("beta_candidate")
    ][:10]
    lines = [
        "# MCP Registry Beta Candidate Report v0.1",
        "",
        f"Generated at: `{datetime.now(UTC).isoformat()}`",
        "",
        "## What This Report Is",
        "",
        "This report summarizes the calibrated `public_beta_mcp` candidate set built from local Official MCP Registry metadata already saved in this repository.",
        "",
        "This report is not a security certification, supplier verification, quality guarantee, purchasing advice, or action permission.",
        "",
        "## Data Source: Official MCP Registry Metadata",
        "",
        f"- Source mode: `{gate.get('source_mode')}`",
        "- No live network, scraping, or link following is performed by this report generator.",
        "- Objects remain `EXTRACTED_UNVERIFIED`.",
        "",
        "## Candidate Gate Definition",
        "",
        "- `PASS_PUBLIC_BETA_CANDIDATE` means the record can appear as registry metadata in beta surfaces.",
        "- It does not mean `VERIFIED`, `ACTION_READY`, safe, secure, maintained, or high quality.",
        "- Missing pricing or policy fields are warnings/HOLD context for MCP registry metadata, not automatic blocks.",
        "",
        "## Candidate Count",
        "",
        f"- Registry objects: `{gate.get('object_count', 0)}`",
        f"- Source traces: `{gate.get('trace_count', 0)}`",
        f"- Public beta MCP candidates: `{candidate_count}`",
        "",
        "## Not Verified / Not Security Certified",
        "",
        "- `verified=false` for all candidates.",
        "- `action_ready=false` for all candidates.",
        "- `not_security_certified=true` for the dataset.",
        "- Registry metadata is not supplier verified.",
        "",
        "## Top Example Beta Candidates",
        "",
    ]
    if candidates:
        lines.extend(f"- `{item['object_id']}` - `{item['status_to_display']}`" for item in candidates)
    else:
        lines.append("- No beta candidates are available from the current local registry files.")
    lines.extend(
        [
            "",
            "## Missing Fields",
            "",
            f"- Missing field stats: `{audit.get('missing_field_stats', {})}`",
            "",
            "## Quality Audit Summary",
            "",
            f"- Source trace coverage: `{audit.get('source_trace_coverage')}`",
            f"- Objects with repositories: `{audit.get('objects_with_repository')}`",
            f"- Objects with packages: `{audit.get('objects_with_packages')}`",
            f"- Hold counts: `{audit.get('hold_counts')}`",
            f"- Block counts: `{audit.get('blocked_counts')}`",
            "",
            "## How To Use `data_scope=public_beta_mcp`",
            "",
            "Use the REST API, MCP tools, or HF demo with `data_scope=public_beta_mcp`. If no candidate rows are available, the surfaces return a warning rather than falling back to fake sample records.",
            "",
            "## Limitations",
            "",
            "- Registry metadata may be incomplete or stale.",
            "- AOI does not fetch repository, package, docs, or security pages in Package 7F.",
            "- Source traces support registry metadata fields but do not prove currentness or correctness.",
            "- Missing pricing and policy fields are common for MCP registry records.",
            "",
            "## Not Implemented",
            "",
            "- live network",
            "- broad crawling",
            "- arbitrary scraping",
            "- link following",
            "- external LLM calls",
            "- supplier verification",
            "- security certification",
            "- payment, booking, login, email, form submission, purchase, account connection, or contract signing",
        ]
    )
    return "\n".join(lines) + "\n"


def write_registry_beta_report(path: str | Path = DEFAULT_OUTPUT) -> Path:
    destination = _resolve(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(generate_registry_beta_report(), encoding="utf-8")
    return destination


def main() -> None:
    path = write_registry_beta_report()
    print(f"Saved MCP registry beta report: {path}")


if __name__ == "__main__":
    main()
