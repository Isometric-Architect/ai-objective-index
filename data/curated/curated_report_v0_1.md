# Curated Data Report v0.1

Generated at: `2026-05-18T10:25:30.707710+00:00`

## What Curated Data Is

Curated data is manually entered candidate data for real AI tools, APIs, SaaS products, and MCP servers. The current seed may contain placeholder examples only.

## Why It Is Separate

Curated data is separate from fake sample data and local generated fixture extraction data. Public beta scope is curated-only by default to avoid presenting fake samples as public beta records.

## Current Counts

- Curated object count: `1`
- Source trace count: `1`
- Public beta ready count: `0`

## Evidence Gate Summary

- Pass count: `0`
- Hold count: `1`
- Block count: `0`
- Token counts: `{'HOLD_PLACEHOLDER': 1}`

## Missing Fields Summary

- Missing field counts: `{'refund_policy': 1, 'data_retention_policy': 1}`

## Known Limitations

- Curated objects are not supplier verified.
- Source traces are required but do not prove completeness, correctness, legal sufficiency, or currentness.
- Placeholder records are not public beta candidates.
- No live crawling.
- No network fetch.

## How To Add Curated Objects Manually

1. Add rows to `data/curated/curated_objects_v0_1.jsonl`.
2. Add field-level traces to `data/curated/curated_source_traces_v0_1.jsonl`.
3. Run `python -m ai_objective_index.curated_index_export`.
4. Run `python -m ai_objective_index.curated_eval`.
5. Run `python -m ai_objective_index.curated_report_generator`.
