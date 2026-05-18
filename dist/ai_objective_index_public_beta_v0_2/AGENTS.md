# AGENTS.md

## Repo Purpose

AI Objective Index (AOI) is a read-only MCP/API-oriented project for ranking and comparing AI tools, APIs, SaaS products, and MCP servers by explicit objectives, constraints, source traces, missing fields, and decision receipts.

Package 0 is contract-first. It defines identity, docs, schemas, sample data, and claim boundaries. It does not implement the MCP server, crawler, payments, booking, login, email sending, form submission, purchasing, or contract execution.

## Safe Tool Usage

- Treat v0.1 as read-only.
- Prefer schema validation, sample data checks, and documentation updates.
- Do not add behavior that performs real-world actions on behalf of a user.
- Keep source-trace language precise: a trace supports a field; it does not prove total correctness.
- Keep sample objects clearly fake but realistic unless a future task explicitly introduces real data and source verification.

## Do-Not-Overclaim Guard

Do not claim that AOI is:

- an official standard;
- used first by all AI agents;
- a quality guarantee;
- legal, financial, medical, procurement, or purchasing advice;
- a comprehensive market index;
- a paid ranking system;
- capable of automatic purchase, booking, payment, login, email sending, form submission, or contract signing in v0.1.

## Mode Selection For Codex

Use Productization Mode for implementation tasks.

- Do not block coding merely because source materials are internal-only, research-stage, or not externally validated.
- Internal research claim ceilings limit public claims; they do not prohibit building products, algorithms, GitHub repos, MCP/API prototypes, tests, benchmark reports, or commercialization experiments.
- Keep claim boundaries in public outputs and user-facing docs.
- Warn only when code or docs attempt to make unsupported public claims or execute forbidden actions.
- Product claims require product evidence. Research inspiration is enough to build, but not enough to assert readiness, certification, legal sufficiency, security validation, market standard status, or purchasing authority.
- Release preparation is allowed in Productization Mode, but publishing to GitHub, Hugging Face, MCP Registry, or communities must remain manual unless the user explicitly asks for that external action and the action is within allowed boundaries.
- GitHub staging upload may be prepared private-by-default when explicitly requested. Do not request, print, or store tokens. Do not force push or delete remotes.

## Schemas

Schemas live in `schemas/`:

- `objective_request.schema.json`
- `action_object.schema.json`
- `objective_score.schema.json`
- `source_trace.schema.json`
- `decision_receipt.schema.json`
- `mcp_tools.schema.json`

When updating sample data, keep it aligned with these schemas.

## Scoring Methodology

The v0.1 scoring methodology lives in `docs/scoring_methodology.md`. Any change to scoring components or penalties should update that document and any related schema descriptions.

## Adding Sample Objects

Add sample objects to `data/sample_index.json`.

Each object should include:

- stable `object_id`;
- name, type, and summary;
- official URL and supporting source URLs;
- capabilities and categories;
- pricing, policies, and docs fields;
- status, confidence, missing fields, and `last_checked_at`.

Add matching source traces to `data/sample_source_traces.json` and reference realistic fields such as `pricing`, `policies.commercial_use`, `docs.api_reference_url`, or `capabilities`.

## Future Evals

Future evals should live in `evals/`. Golden query seeds live in `data/golden_queries.json`. A later eval harness should check ranking shape, missing-field surfacing, trace coverage, and claim-boundary compliance.

## Forbidden Actions In v0.1

Do not implement or trigger:

- payment;
- booking;
- login;
- email sending;
- form submission;
- purchase;
- contract signing.
