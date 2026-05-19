from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from ai_objective_index.missing_fields import list_missing_fields

from .mcp_registry_evidence_gate import validate_registry_dataset
from .mcp_registry_loader import load_registry_objects, load_registry_source_traces


DEFAULT_OUTPUT = Path("data/registry/mcp_registry_report_v0_1.md")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def generate_mcp_registry_report() -> str:
    objects = load_registry_objects()
    traces = load_registry_source_traces()
    validation = validate_registry_dataset(objects, traces)
    fixture_only = any(bool(getattr(item, "fixture_only", False)) for item in objects)
    missing = Counter(
        field.field
        for action_object in objects
        for field in list_missing_fields(action_object)
    )
    top = sorted(objects, key=lambda item: item.confidence, reverse=True)[:5]
    lines = [
        "# MCP Registry Intake Report v0.1",
        "",
        f"Generated at: `{datetime.now(UTC).isoformat()}`",
        "",
        "## What This Report Is",
        "",
        "This report summarizes AOI Package 7D intake of Official MCP Registry-style metadata into local read-only AOI records.",
        "",
        "## Data Source",
        "",
        "- Source mode: `fixture`" if fixture_only else "- Source mode: `official_mcp_registry_api`",
        "- Default execution is offline fixture mode.",
        "",
        "## Scope",
        "",
        "- Object type: `MCPServer`",
        "- Status: `EXTRACTED_UNVERIFIED`",
        "- No live crawling / no scraping.",
        "",
        "## Object Counts",
        "",
        f"- Registry object count: `{len(objects)}`",
        f"- Source trace count: `{len(traces)}`",
        f"- Public beta ready count: `{validation['public_beta_ready_count']}`",
        "",
        "## Evidence Gate Summary",
        "",
        f"- Pass count: `{validation['pass_count']}`",
        f"- Hold count: `{validation['hold_count']}`",
        f"- Block count: `{validation['block_count']}`",
        f"- Token counts: `{json.dumps(validation['token_counts'], ensure_ascii=False)}`",
        "",
        "## Top Example Objects",
        "",
    ]
    if top:
        lines.extend(f"- `{item.object_id}` - {item.name} (`{item.status}`)" for item in top)
    else:
        lines.append("- No registry objects available.")
    lines.extend(
        [
            "",
            "## Missing Fields Summary",
            "",
            f"- Missing field counts: `{dict(missing)}`",
            "",
            "## Limitations",
            "",
            "- Registry metadata is not supplier verified by AOI.",
            "- AOI does not claim the servers are safe, secure, maintained, or high quality.",
            "- This is not a security certification.",
            "- Source traces support fields but do not prove completeness or currentness.",
            "- Fixture mode records are not promoted to `public_beta_mcp`.",
            "- No live crawling / no scraping.",
            "",
            "## Not Implemented",
            "",
            "- broad crawling",
            "- arbitrary website scraping",
            "- link following",
            "- external LLM calls",
            "- payment, booking, login, email sending, form submission, purchase, account connection, supplier verification, or contract signing",
        ]
    )
    return "\n".join(lines) + "\n"


def write_mcp_registry_report(path: str | Path = DEFAULT_OUTPUT) -> Path:
    destination = _resolve(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(generate_mcp_registry_report(), encoding="utf-8")
    return destination


def main() -> None:
    path = write_mcp_registry_report()
    print(f"Saved MCP registry report: {path}")


if __name__ == "__main__":
    main()

