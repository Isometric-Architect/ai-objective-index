from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .curated_loader import load_curated_objects, load_curated_source_traces
from .curated_validator import validate_curated_dataset
from .missing_fields import list_missing_fields


DEFAULT_OUTPUT = Path("data/curated/curated_report_v0_1.md")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def generate_curated_report() -> str:
    objects = load_curated_objects()
    traces = load_curated_source_traces()
    validation = validate_curated_dataset(objects, traces)
    missing = Counter(
        field.field
        for action_object in objects
        for field in list_missing_fields(action_object)
    )
    lines = [
        "# Curated Data Report v0.1",
        "",
        f"Generated at: `{datetime.now(UTC).isoformat()}`",
        "",
        "## What Curated Data Is",
        "",
        "Curated data is manually entered candidate data for real AI tools, APIs, SaaS products, and MCP servers. The current seed may contain placeholder examples only.",
        "",
        "## Why It Is Separate",
        "",
        "Curated data is separate from fake sample data and local generated fixture extraction data. Public beta scope is curated-only by default to avoid presenting fake samples as public beta records.",
        "",
        "## Current Counts",
        "",
        f"- Curated object count: `{len(objects)}`",
        f"- Source trace count: `{len(traces)}`",
        f"- Public beta ready count: `{validation['public_beta_ready_count']}`",
        "",
        "## Evidence Gate Summary",
        "",
        f"- Pass count: `{validation['pass_count']}`",
        f"- Hold count: `{validation['hold_count']}`",
        f"- Block count: `{validation['block_count']}`",
        f"- Token counts: `{validation['token_counts']}`",
        "",
        "## Missing Fields Summary",
        "",
        f"- Missing field counts: `{dict(missing)}`",
        "",
        "## Known Limitations",
        "",
        "- Curated objects are not supplier verified.",
        "- Source traces are required but do not prove completeness, correctness, legal sufficiency, or currentness.",
        "- Placeholder records are not public beta candidates.",
        "- No live crawling.",
        "- No network fetch.",
        "",
        "## How To Add Curated Objects Manually",
        "",
        "1. Add rows to `data/curated/curated_objects_v0_1.jsonl`.",
        "2. Add field-level traces to `data/curated/curated_source_traces_v0_1.jsonl`.",
        "3. Run `python -m ai_objective_index.curated_index_export`.",
        "4. Run `python -m ai_objective_index.curated_eval`.",
        "5. Run `python -m ai_objective_index.curated_report_generator`.",
    ]
    return "\n".join(lines) + "\n"


def write_curated_report(path: str | Path = DEFAULT_OUTPUT) -> Path:
    destination = Path(path)
    if not destination.is_absolute():
        destination = _repo_root() / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(generate_curated_report(), encoding="utf-8")
    return destination


def main() -> None:
    path = write_curated_report()
    print(f"Saved curated report: {path}")


if __name__ == "__main__":
    main()
