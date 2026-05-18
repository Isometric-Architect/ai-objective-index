# Package 6C Generated Extraction Integration

Package 6C integrates Package 6A generated fixture extraction outputs into AOI helper flows without enabling live crawling.

## What It Does

- Loads generated `ActionObject` records from `data/generated/extracted_objects_v0_2.json`.
- Loads generated `SourceTrace` records from `data/generated/extracted_source_traces_v0_2.json`.
- Builds explicit `sample`, `generated`, and `integrated` stores.
- Exports integrated JSON files.
- Runs integrated local evals.
- Generates an integrated Markdown report.
- Adds optional `data_scope` support to REST and MCP helpers while keeping `sample` as the default.

## Why Generated Records Stay EXTRACTED_UNVERIFIED

Generated records come from local fixtures and rule-based extraction. They may have source traces and confidence values, but they are not verified supplier claims. They remain `EXTRACTED_UNVERIFIED` unless a future verified-data package explicitly changes their status.

## Commands

```powershell
python -m ai_objective_index.integrated_index_export
python -m ai_objective_index.integrated_eval
python -m ai_objective_index.integrated_report_generator
```

## Relation To Package 6A

Package 6A creates local fixture extraction outputs. Package 6C makes those outputs searchable, scorable, comparable, exportable, and reportable through explicit integrated helpers.

## No Live Crawling

Package 6C does not fetch network data, run live crawling, call external LLM APIs, publish demos, post to communities, verify suppliers, or perform external actions.

