# Launch Notes

## ROE-10 DataCapsule Pilot Receipt Packager

ROE-10 adds a local/offline DataCapsule pilot receipt bundle for sample corpus manifest review. It does not crawl, fetch URLs, inspect raw private content, upload data, train models, call external APIs, request tokens, prove legal/privacy/license/evaluation-cleanliness status, certify data quality, or authorize training/actions.

## ROE-9 QIRA Pilot Receipt Packager

ROE-9 adds a local/offline QIRA-Code ReleaseGate pilot receipt bundle for sample code-change review. It does not call GitHub APIs, post comments, mutate external repositories, merge, deploy, publish packages, request tokens, prove code correctness, certify security, guarantee quality, or authorize actions.

## ROE-8 AgentSec Pilot Receipt Packager

ROE-8 adds a local/offline AgentSec pilot receipt bundle for sample manifest review. It does not call live MCP servers, execute tools, call GitHub APIs, post comments, modify external repositories, request tokens, certify security, guarantee quality, prove compliance, or authorize actions.

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

## Package 8D GitHub Private Staging QA

Package 8D verifies the GitHub private staging repository and binds the real GitHub URL into local materials.

It does not make the repository public, create a release, upload to Hugging Face, post to communities, submit to MCP Registry, crawl, scrape, or perform external actions.

## Package 8F Hugging Face Manual Upload Bundle

Package 8F prepares `hf_upload/space/` and `hf_upload/dataset/` for manual Hugging Face web upload.

It does not upload, use tokens, store secrets, make GitHub public, post to communities, submit to MCP Registry, crawl, scrape, fetch network data, or perform external actions.

## Package 8G Hugging Face Private Upload

Package 8G adds token-safe Hugging Face authentication checks, private-only Space/Dataset upload helpers, fallback browser instructions, and post-upload QA.

The default is dry-run. Execute mode requires existing local Hugging Face authentication and keeps both repos private. Package 8G does not print or store tokens, make Hugging Face repos public, post to communities, submit to MCP Registry, crawl, scrape, or perform external actions.

## Package 8H Private Deployment Sync

Package 8H binds the private GitHub and Hugging Face URLs into local docs and release materials, verifies private deployment status, audits crosslinks, and can push the private sync to GitHub.

It does not make GitHub or Hugging Face public, create a GitHub release, post to communities, submit to MCP Registry, crawl, scrape, follow links, print/store tokens, force push, or perform external actions.

## Package 8I Public Launch Decision Gate

Package 8I adds a dry-run public launch gate, guarded visibility switch helper, public claim audit, private reviewer draft, announcement drafts, and token revocation checklist.

It does not make anything public by default. Execute mode requires `AOI_PUBLIC_LAUNCH_CONFIRM=YES` and a passing launch gate. Package 8I does not post to communities, submit to MCP Registry, create a GitHub Release, crawl, scrape, follow links, print/store tokens, force push, or perform external actions.

## Package 8I-R No-Contact Public Beta Gate

Package 8I-R replaces private-reviewer dependency with deterministic local reviewer simulation and GitHub Issue feedback. It is useful when the owner has no private reviewers available.

The no-contact path runs AI/self-review checks, packages issue labels and golden queries, guards public beta messages, and writes a no-contact GO/NO-GO decision file.

It does not make anything public by default, post to communities, submit to MCP Registry, call external LLM APIs, crawl, scrape, follow links, print/store tokens, or claim verification, safety, security certification, quality guarantee, production readiness, purchasing advice, or action permission.

## Package 8J Pre-Public Sync

Package 8J syncs no-contact launch materials to private staging when explicitly run with `--execute`, then writes a final public dry-run and pre-public state report.

It does not make GitHub public, make Hugging Face public, create a GitHub Release, post to communities, submit to MCP Registry, crawl, scrape, follow links, print/store tokens, force push, or perform external actions.

## Package 8K Public Visibility Switch

Package 8K performs the public visibility switch after explicit confirmation through `AOI_PUBLIC_LAUNCH_CONFIRM=YES`.

It may make the prepared GitHub repository, Hugging Face Space, and Hugging Face Dataset public. It does not post to communities, create a GitHub Release, submit to MCP Registry, crawl, scrape, follow links, print/store tokens, force push, or perform external actions.

## Package 8L Post-Public Stabilization

Package 8L runs the first public-stage stabilization pass. It checks public records, activates GitHub issue templates and suggested labels, writes manual token revocation guidance, and creates a 72-hour observation plan.

It does not post to communities, create a GitHub Release, submit to MCP Registry, revoke tokens automatically, crawl, scrape, follow links, print/store tokens, force push, or perform external actions.

## Package 8M Public Ops Baseline

Package 8M adds the public operations baseline, dirty-worktree hygiene classification, GitHub issue label plan, 72-hour observation log scaffold, and next decision gate.

It does not post to communities, create a GitHub Release, submit to MCP Registry, delete generated files, crawl, scrape, follow links, print/store tokens, force push, or perform external actions.

## Hugging Face Parquet Converter Notification

Hugging Face created `refs/convert/parquet` for `edict-lab/ai-objective-index-sample` through the `parquet-converter` bot. This records that Dataset Viewer and Parquet access are available.

No action is required. This event does not imply dataset quality, verification, security certification, supplier verification, a quality guarantee, or purchasing advice.

## Package 8N Public Observation Runner

Package 8N starts the active 72-hour public observation workflow, records a 0-hour public metrics snapshot, writes 24/48/72-hour templates, reviews residual worktree changes, and gates the next decision.

It does not post to communities, create a GitHub Release, submit to MCP Registry, delete residual files, stage all changes, force push, crawl, scrape, follow links, print/store tokens, or perform external actions.

## Package 8O Public Beta Launch Wave 1

Package 8O prepares the first conservative public beta wave: GitHub prerelease notes, feedback drafts, optional safe discussion handling, MCP Registry server JSON draft, submission gate, and launch report.

It does not auto-post to HN, Reddit, OpenAI Developer Community, Product Hunt, or MCP community sites. It does not submit to MCP Registry unless eligibility passes and explicit confirmation is present.

## Package 8P MCP Registry PyPI Readiness

Package 8P prepares PyPI package readiness, a `registryType: pypi` server JSON candidate, MCP Registry publish readiness checks, upload instructions, and a manual community post queue.

It does not upload to PyPI/TestPyPI, submit to MCP Registry, auto-post to communities, broaden Hugging Face token scopes, print/store tokens, crawl, scrape, follow links, or perform external actions.

## Package 8Q-A Local Build Readiness

Package 8Q-A checks and installs local packaging tools if requested, builds local dist artifacts, runs `twine check`, runs a local install smoke, and refreshes PyPI readiness.

It does not upload to TestPyPI/PyPI, submit to MCP Registry, request/print/store tokens, post to communities, crawl, scrape, follow links, or perform forbidden actions.

## Package 9A AOI vNext Alignment

Package 9A reframes AOI vNext as an AI Agent Capability Trust Router: a trust/routing layer above registries that maps agent objectives to source-traced capability candidates with residual risk and usage boundaries.

It adds vNext model/schema drafts and claim-boundary docs. It pauses PyPI upload and MCP Registry submission until vNext alignment is complete.

## Package 9F vNext Distribution Gate

Package 9F audits distribution surfaces after Capability Trust, Objective Router, ExecutionReceipt memory, and local Probe-before-Use are present.

It does not build or upload packages, submit MCP Registry metadata, post to communities, call live MCP servers, execute external tools, fetch URLs, or request tokens. It recommends a version decision before the 8Q-A local build path resumes.

## Package 8Q-A Resumed

Package 8Q-A resumed applies `0.3.0a1` for the first vNext local build candidate, builds wheel/sdist artifacts, runs `twine check`, runs local install smoke checks, and refreshes PyPI/MCP Registry readiness. It still performs no TestPyPI/PyPI upload, no MCP Registry submission, and no token handling.

## Package 8Q-C-alt Real PyPI Direct Gate

Package 8Q-C-alt exists because TestPyPI signup is blocked for the owner. It adds a strict real PyPI direct upload gate, a token-safe interactive twine upload runner, real PyPI install verification, release audit, and a post-PyPI MCP Registry gate.

It does not use TestPyPI, submit MCP Registry metadata, post to communities, create `.pypirc`, pass tokens through command-line flags, print/store tokens, or claim verification, safety, security certification, quality guarantee, product readiness, or purchasing advice.

## Package 8R MCP Registry Publish Gate

Package 8R prepares Official MCP Registry publication after the real PyPI `0.3.0a1` upload and install verification. It checks `mcp-publisher`, audits `.mcp/server.json`, writes a dry-run result, and provides post-publish verification/audit helpers.

It does not submit MCP Registry metadata unless every gate passes and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set. It does not upload a new PyPI version, post to communities, print/store tokens, or claim verification, safety, security certification, quality guarantee, product readiness, purchasing advice, or action authorization.

## Package 8S Technology Protection

Package 8S audits public surfaces and package artifacts before increasing exposure through MCP Registry. It defines a public/private split, checks for private kernel disclosure, inspects wheel/sdist contents where available, assesses clone risk, records license/IP positioning, and writes a pre-publish protection gate.

It does not submit MCP Registry metadata, install or execute `mcp-publisher`, upload a new PyPI version, expose private kernel values, request/print/store tokens, or claim verification, safety, security certification, quality guarantee, product readiness, purchasing advice, or action authorization.

## Package 8R-B MCP Registry Submit

Package 8R-B adds the guarded publisher setup, GitHub auth, preflight, dry-run, execute, reconcile, and discovery-report path for MCP Registry publication.

It does not publish unless all gates pass and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set. It does not modify PyPI, post to communities, print/store tokens, expose private kernel details, or claim Registry publication is verification, security certification, quality guarantee, product readiness, purchasing advice, or action authorization.
