# Quickstart

AI Objective Index (AOI) package 0 is a contract package. It is useful for reviewing the project boundary, validating sample data shape, and preparing future read-only MCP/API behavior.

## 1. Inspect The Schemas

Start with:

- `schemas/objective_request.schema.json`
- `schemas/action_object.schema.json`
- `schemas/objective_score.schema.json`
- `schemas/source_trace.schema.json`
- `schemas/decision_receipt.schema.json`
- `schemas/mcp_tools.schema.json`

## 2. Inspect Sample Data

Sample data lives in:

- `data/sample_index.json`
- `data/sample_source_traces.json`
- `data/golden_queries.json`

The objects are fake but realistic. They are designed for contract testing, not product claims.

## 3. Validate JSON

Use Python's built-in JSON parser:

```powershell
python -m json.tool data/sample_index.json
python -m json.tool data/sample_source_traces.json
python -m json.tool data/golden_queries.json
```

## 4. Read The Boundaries

Before using AOI output in an agent flow, read:

- `docs/scoring_methodology.md`
- `docs/source_trace_methodology.md`
- `docs/claim_boundaries.md`

AOI v0.1 is read-only and does not execute payments, bookings, logins, emails, forms, purchases, or contracts.

