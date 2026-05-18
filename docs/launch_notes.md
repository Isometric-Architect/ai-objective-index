# Launch Notes

## Package 0

Package 0 establishes the AOI identity and contract surface:

- project README and governance docs;
- read-only v0.1 claim boundaries;
- JSON Schemas;
- fake but realistic sample data;
- mock source traces;
- golden query seeds;
- placeholder folders for reports, evals, and examples.

## Launch Positioning

AOI is a read-only objective ranking and comparison layer for AI agents. It helps agents explain why an AI tool, API, SaaS product, or MCP server appears to fit a stated objective from available data and traces.

AOI should be launched as a productization prototype: internal research concepts may guide implementation, but public claims must be limited to what the product actually validates.

## What Is Not Included

Package 0 does not include:

- production MCP server;
- HTTP API implementation;
- crawler;
- real-data ingestion;
- payment, booking, login, email, form submission, purchase, or contract execution workflows.

## Package 4 Launch Posture

Package 4 makes AOI launchable as a benchmark-style MCP/API tool by adding golden query evals, downloadable JSON files, and Markdown reports.

The recommended v0.1 posture is: please test and break the golden queries. The goal is not hype or a claim of official ranking authority. The goal is to make ranking behavior inspectable, identify weak fields, and improve source-trace coverage.

All Package 4 reports must preserve the claim boundary: benchmark outputs are not quality guarantees, official rankings, legal advice, purchasing advice, or safety certifications.

## Package 5 Launch Posture

Package 5 packages the project for community testing: local Hugging Face demo draft, dataset card draft, example clients, issue templates, and launch copy.

The posture remains benchmark + failure loop, not hype. Publishing and community posting are manual. No tokens, credentials, crawler, or external action automation are required.

## Package 6A Crawler / Extractor Skeleton

Package 6A introduces the acquisition layer as local/fixture-first infrastructure. It is not a live broad crawler.

The posture remains benchmark + failure loop, not hype. The crawler/extractor should make extraction failures visible, attach source traces to extracted fields, and default generated records to `EXTRACTED_UNVERIFIED`.

Network fetch is disabled by default. Any future live acquisition should remain public-data oriented, respect robots.txt, use conservative rate limits, avoid login/paywall/private data, and preserve all v0.1 forbidden-action boundaries.

## Package 6C Generated Integration

Package 6C integrates generated fixture extraction outputs into local store, eval, export, report, API, and MCP helper flows.

Generated data is local fixture extraction only and not live web crawl output. The status `EXTRACTED_UNVERIFIED` should stay visible in launch copy and reports. It means source-traced but not supplier-verified.

The launch posture remains benchmark + failure loop, not hype. No live crawling, network fetching, external LLM extraction, supplier verification, publishing, posting, payment, booking, login, email sending, form submission, purchase, or contract signing is included.

## Package 6D-S Source-Governed Upgrade

Package 6D-S adds source-status-before-evidence checks, validator-before-claim promotion gates, use-right separation, claim ceilings, action-boundary blocks, obstruction certificates, and false-closure negative controls.

The launch posture remains benchmark + failure loop, not hype. The new controls are meant to prevent silent BOX or false closure: a missing price, missing policy, stale source, unverified generated record, or blocked action must stay visible as HOLD or BLOCK with a next evidence step.

## Productization Mode

Future AOI development should default to Productization Mode for implementation tasks. Research claim ceilings prevent unsupported external claims; they do not prevent building software, algorithms, MCP/API prototypes, benchmark demos, GitHub repositories, or commercialization experiments.

Public launch copy should use Product Claim Mode: describe implemented read-only behavior, benchmark scope, source traces, missing fields, and limitations. Do not claim product readiness, certification, official standard status, purchasing advice, or action execution without product evidence.

## Package 6D Beta Readiness

Package 6D checks beta readiness for local `sample`, `generated`, and `integrated` data scopes across Core, MCP, REST API, OpenAPI, Hugging Face demo, examples, evals, reports, and docs.

Beta readiness remains local-only. Package 6D does not perform public release, live crawling, network fetch, Hugging Face publishing, community posting, supplier verification, payment, booking, login, email, form submission, purchase, account connection, or contract signing.

## Package 7B Public Beta Release Candidate

Package 7B prepares a local public beta release candidate pack and automated readiness audit.

It does not publish to GitHub, publish to Hugging Face, post to communities, submit to MCP Registry, crawl live sites, fetch network data, call external LLM APIs, or execute external actions.

## Package 7C Curated Seed Expansion

Package 7C adds a manual curated seed path for real-object candidates and a conservative evidence gate for the `public_beta` data scope.

Curated data is not supplier verified. The `public_beta` scope is curated-only by default and should warn when no curated object passes the evidence gate. This improves release preparation without live crawling, scraping, network fetch, external LLM calls, supplier verification, publishing, posting, or external action execution.

## Package 7D MCP Registry Intake

Package 7D adds a narrow Official MCP Registry intake pilot. Default mode is offline fixture mode. Live registry access requires explicit `--allow-network`, uses read-only API GET requests only, and is not run as part of default verification.

The `mcp_registry` scope exposes local registry intake records. The `public_beta_mcp` scope contains only registry records that pass the evidence gate; in fixture mode it may be empty and should warn clearly.

Registry metadata remains `EXTRACTED_UNVERIFIED`. It is not supplier verification, not a security certification, not a quality guarantee, and not permission to execute external actions.

## Package 7E Live Registry Run

Package 7E adds a controlled run wrapper for Official MCP Registry live intake. Default mode is still no-network. The live path requires `--allow-network`, records a run receipt, uses only read-only `GET /v0.1/servers?limit=50`, and never follows links or fetches repository/package/docs pages.

If live access fails, AOI writes manual fallback status with the next action: download the registry JSON and save it as `data/registry/mcp_registry_raw_v0_1.json`.

## Package 7F Registry Candidate Gate

Package 7F calibrates `public_beta_mcp` into a beta candidate set based on saved MCP Registry metadata.

The launch posture remains careful: `REGISTRY_METADATA_CANDIDATE` is not `VERIFIED`, not `ACTION_READY`, not supplier verification, not security certification, not a quality guarantee, not purchasing advice, and not action permission. Package 7F does not run live network, crawl, scrape, follow links, publish, or execute external actions.

## Package 7G Real Registry Payload Activation

Package 7G makes real/manual registry raw payloads durable. Fixture data must not silently overwrite a real `mcp_registry_raw_v0_1.json`, and `public_beta_mcp` must not be built from fixture records.

The launch posture remains local and evidence-labeled: activate manual raw, audit payload mode, reprocess outputs, and keep all records `EXTRACTED_UNVERIFIED`.

## Package 8A Real-Data Public Beta Preflight

Package 8A adds final real-data public beta preflight. It regenerates local v0.2 release assets from the activated Official MCP Registry metadata candidates.

No publishing, additional live network, crawling, scraping, link following, registry submission, or external action is performed.

## Package 8B Manual Launch Workspace

Package 8B prepares local launch execution assets, no-secrets checks, claim guards, dry-run output, and a local archive.

It does not publish, upload, post, submit to MCP Registry, run live network, crawl, scrape, follow links, or execute external actions.
