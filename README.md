# AI Objective Index
<!-- mcp-name: io.github.Isometric-Architect/ai-objective-index -->

AI Objective Index (AOI) is a read-only MCP/API data contract and vNext AI Agent Capability Trust Router for routing explicit objectives to source-traced capability candidates with constraints, missing fields, route decisions, local receipt memory, and local metadata probes.

## Why This Exists

AI agents increasingly need to choose between tools. A generic web search result, sponsored directory, or untraced recommendation is not enough when the agent must explain why one option fits an objective better than another. AOI exists to make those comparisons explicit, auditable, and bounded.

AOI is not a generic web search engine. It is not a supplier-submitted directory. It is not a paid ranking system. It is not a payment, booking, email, login, form submission, purchase, or contract execution platform.

AOI is a productization prototype built from internal research concepts. Internal research claim ceilings do not prohibit implementation; they prevent unsupported external claims about readiness, guarantees, certification, or authority.

## Current Scope

Package 0 defines the v0.1 project identity, schemas, documentation, sample data contract, and claim boundaries for the first vertical: AI tools, APIs, SaaS products, and MCP servers.

v0.1 is read-only. Package 1 adds the local core engine, Package 2 adds read-only MCP tool functions, and Package 3 adds a read-only FastAPI REST API. Package 6A adds a crawler/extractor skeleton and fixture pipeline, but it does not run broad live crawling. This repository still does not implement a production ingestion pipeline, payment flow, booking flow, account login, email sender, form submitter, purchasing system, supplier claim/verify flow, profile modification, or contract workflow.

vNext adds conservative routing surfaces: Capability Trust, Objective Router, ExecutionReceipt memory, and local-only Probe-before-Use. These are source-traced route-decision aids, not verification, safety certification, quality guarantee, product readiness, live security scanning, external gateway execution, or action authorization.

ROE-0 adds a parallel ResidualOps productization plan for QIRA-Code ReleaseGate, AgentSec Gate, and DataCapsule / AIDREG Engine. The public repository may expose high-level packet, residual, receipt, and ALLOW/HOLD/BLOCK language, while ranking calibration, threshold policy, anti-gaming rules, provider priors, private negative controls, private probe seeds, and commercial routing policy remain non-public.

QIRA-1 adds the first ResidualOps vertical MVP: a local/offline QIRA-Code ReleaseGate that creates behavior contracts, patch candidates, validator packets, residual ledgers, patch receipts, and action licenses. It does not execute arbitrary external tools, deploy code, request tokens, certify security, guarantee quality, or approve production use.

QIRA-2 adds local JSON task-packet intake for QIRA. A user can provide task, expected behavior, changed files or patch diff text, test summary, and declared claims; QIRA emits a local release-gate report without applying patches, executing tests, deploying code, contacting external services, or handling secrets.

QIRA-3 adds local patch path classification and test-command contracts. It records which files changed and which project-supplied commands would need review, but it still does not execute commands, apply patches, deploy code, contact external services, or handle secrets.

QIRA-4 adds a reusable GitHub Action dry-run wrapper under `.github/actions/qira-releasegate-dry-run/`. It is not an auto-enabled workflow; the example workflow stays in `examples/` until a repository owner intentionally enables it.

QIRA-5 adds a local PR diff/changed-file packet generator. It turns repository-supplied diff text or changed-file metadata into a conservative QIRA task packet and optional QIRA-3 review output without calling GitHub APIs, running `git`, applying patches, executing tests, deploying code, handling tokens, or publishing anything.

QIRA-6 adds CI evidence intake. It accepts repository-supplied CI result metadata, validates the recorded commands and statuses, and can close the local test-evidence gap for scoped QIRA review without QIRA running tests, calling GitHub APIs, inspecting live CI, merging, deploying, handling tokens, or authorizing production actions.

QIRA-7 adds an opt-in GitHub CI evidence bridge. It provides a reusable composite action and example workflow that pass repository-owned CI status metadata into QIRA-6, while keeping workflows disabled by default and preserving no-GitHub-API/no-token/no-merge/no-deploy boundaries.

QIRA-8 adds reviewer-facing PR artifacts: a Markdown reviewer report, PR comment draft, artifact manifest, and bundle result. It writes local artifacts only and does not post comments, call GitHub APIs, execute commands, merge, deploy, upload, publish, or handle tokens.

QIRA-9 adds an opt-in workflow artifact template for repository owners who want QIRA local review artifacts from repository-owned CI evidence. The workflow remains in `examples/` and is not active by default. QIRA-9 does not post comments, call GitHub APIs on behalf of QIRA, apply patches, merge, deploy, upload packages, publish registry metadata, handle tokens, certify security, guarantee quality, prove product readiness, or authorize actions.

AgentSec-1 starts the second ResidualOps vertical: a local/offline MCP/tool manifest risk packet scanner. It hashes repository-supplied metadata, records permission scope indicators, hidden-instruction signals, namespace review signals, forbidden action language, and unsupported claims. It does not call live MCP servers, execute tools, fetch URLs, handle tokens, act as a security gateway, certify security, guarantee quality, claim product readiness, or authorize external actions.

AgentSec-2 adds local multi-manifest intake and public-safe policy profiles. It can summarize ALLOW metadata-only, HOLD review-required, and BLOCK policy-risk decisions across a supplied manifest set, while keeping exact private thresholds, provider priors, anti-gaming rules, private negative controls, and commercial routing policy non-public.

AgentSec-3 adds an opt-in CI artifact bridge. It provides a reusable composite action and inactive example workflow that convert repository-supplied MCP/tool manifests into AgentSec-2 policy-gate artifacts. It does not enable workflows by default, call live MCP servers, execute tools, fetch URLs, call GitHub APIs, post comments, handle tokens, certify security, guarantee quality, or authorize actions.

AgentSec-4 adds public-safe policy profile packs and static MCP manifest hardening for AOI's read-only MCP surfaces. It does not call live MCP servers, execute tools, fetch URLs, request tokens, expose private thresholds or provider priors, certify security, guarantee quality, prove product readiness, or authorize actions.

AgentSec-5 adds a public-safe fake manifest fixture corpus and local negative-control pack. It checks that risky MCP/tool manifest patterns do not slip into `ALLOW_METADATA_ONLY` under the public scanner/profile. It does not call live MCP servers, execute tools, fetch URLs, request tokens, expose private negative-control banks, certify security, guarantee quality, prove product readiness, or authorize actions.

AgentSec-6 adds local manifest corpus ingestion for repository-supplied MCP/tool metadata. It can read a JSON manifest object, JSON list, corpus file, or local directory of JSON manifests, then emits a corpus-level policy-gate artifact without calling live MCP servers, executing tools, fetching URLs, handling tokens, certifying security, guaranteeing quality, proving product readiness, or authorizing actions.

AgentSec-7 adds reviewer-facing PR artifacts for AgentSec local manifest review: a Markdown reviewer report, PR comment draft, artifact manifest, and bundle result. It writes local artifacts only and does not post comments, call GitHub APIs, call live MCP servers, execute tools, fetch URLs, handle tokens, certify security, guarantee quality, prove product readiness, or authorize actions.

AgentSec-8 adds an opt-in workflow artifact template for repository owners who want AgentSec local review artifacts from CI. The workflow remains in `examples/` and is not active by default. AgentSec-8 does not post comments, call GitHub APIs on behalf of AgentSec, call live MCP servers, execute tools, fetch URLs, handle tokens, certify security, guarantee quality, prove product readiness, or authorize actions.

DataCapsule-1 starts the third ResidualOps vertical: local data-use capsules for repository-supplied dataset or corpus metadata. It separates `train`, `retrieve`, `evaluate`, `summarize`, `share`, and `act` use boundaries under source, rights, privacy, eval-leak, stale-data, and claim-ceiling limits. It does not crawl, fetch URLs, inspect private data, call external services, certify legal sufficiency, certify privacy compliance, guarantee data quality, clear licenses, prove evaluation cleanliness, or authorize actions.

DataCapsule-2 adds local corpus manifest intake and negative controls. It aggregates repository-supplied file metadata into a corpus-level DataCapsule, checks known-bad local fixtures, and records false-pass counts without crawling directories, reading private file contents, fetching URLs, calling external services, proving rights/privacy/data quality/eval cleanliness, or authorizing actions.

DataCapsule-3 adds CSV/JSONL corpus manifest intake and a local eval-leak separation report. It normalizes repository-supplied tables into the DataCapsule corpus shape and flags direct train/evaluation path overlap, but it does not inspect file contents, crawl, fetch URLs, prove evaluation cleanliness, certify rights/privacy/data quality, or authorize actions.

DataCapsule-4 adds an opt-in CI artifact bridge for repository-supplied corpus manifests. It provides a reusable composite action and inactive example workflow that convert CSV/JSONL/JSON manifests into DataCapsule artifacts, without auto-enabling workflows, calling GitHub APIs, reading private file contents, fetching URLs, handling tokens, proving rights/privacy/data quality/eval cleanliness, or authorizing actions.

DataCapsule-5 adds a public-safe fake use-rights fixture corpus and local negative-control pack. It checks that risky data metadata patterns do not slip into `ALLOW_USE` for the requested use class. It does not crawl, fetch URLs, inspect private data, handle tokens, prove legal sufficiency, certify privacy compliance, guarantee data quality, prove evaluation cleanliness, clear licenses, or authorize actions.

DataCapsule-6 adds reviewer-facing repository corpus audit artifacts for DataCapsule local metadata review: a corpus audit report, review comment draft, artifact manifest, and bundle result. It writes local artifacts only and does not crawl directories, inspect private file contents, fetch URLs, call external services, post comments, handle tokens, prove rights, certify privacy, guarantee data quality, prove evaluation cleanliness, clear licenses, provide purchasing advice, or authorize actions.

DataCapsule-7 adds an opt-in workflow artifact template for repository owners who want DataCapsule local corpus review artifacts from repository-supplied manifests. The workflow remains in `examples/` and is not active by default. DataCapsule-7 does not post comments, call GitHub APIs on behalf of DataCapsule, crawl directories, inspect private file contents, fetch URLs, call external services, handle tokens, prove legal/privacy/license/evaluation status, guarantee data quality, provide purchasing advice, or authorize actions.

ROE-1 aligns QIRA, AgentSec, and DataCapsule under a common ResidualOps surface matrix: packet or manifest intake, local check/probe/review, receipt/result artifact, ALLOW/HOLD/BLOCK decision, opt-in artifact bridge, and claim boundary. Exact weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, and commercial routing policy remain non-public.

ROE-2 adds a shared artifact manifest and local dashboard skeleton across QIRA, AgentSec, and DataCapsule. It indexes existing local result artifacts and status buckets without running probes, enabling workflows, calling GitHub APIs, uploading packages, submitting registry metadata, certifying security, guaranteeing quality, proving product readiness, or authorizing actions.

ROE-3 adds a unified ResidualOps portfolio release kit across QIRA-8, AgentSec-7, and DataCapsule-6. It produces local release notes, a public vertical index, an operator handoff, and a release artifact manifest without enabling workflows, calling GitHub APIs, posting comments, crawling, calling live MCP servers, executing tools, uploading packages, submitting registry metadata, exposing private kernels, certifying security, guaranteeing quality, proving product readiness, proving legal/privacy/license/evaluation status, or authorizing actions.

ROE-4 aligns the public/private distribution split across QIRA-9, AgentSec-8, and DataCapsule-7. It treats opt-in workflow artifact examples as public-safe distribution surfaces while keeping exact weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, receipt weighting, and commercial routing policy non-public. It does not enable workflows, call GitHub APIs, post comments, execute tools, submit registries, handle tokens, certify security, guarantee quality, prove readiness, or authorize actions.

ROE-5 adds a portfolio onboarding kit for the first external or separate-repository pilot. It creates a vertical selection matrix, owner consent gate, repository pilot checklist, and dry-run onboarding plan while keeping owner consent required before any workflow enablement. It does not enable workflows, call GitHub APIs, post comments, handle tokens, expose private kernels, certify security, guarantee quality, prove readiness, or authorize actions.

ROE-6 adds local pilot receipt intake and feedback memory for future owner-consented repository pilots. It creates a public-safe pilot receipt template, intake gate, feedback memory summary, and claim audit without enabling workflows, calling GitHub APIs, posting comments, storing tokens, exposing private kernels, certifying security, guaranteeing quality, proving readiness, or authorizing actions.

ROE-7 adds pilot receipt readout and a second-run decision gate. It keeps the gate on HOLD until at least one accepted non-secret pilot receipt exists, and it still does not enable workflows, call GitHub APIs, post comments, store tokens, expose private kernels, certify security, guarantee quality, prove readiness, or authorize actions.

ROE-8 adds the first AgentSec pilot receipt packager. It packages a local/offline AgentSec manifest review into a redacted receipt bundle, reviewer readout, feedback memory entry, and gate result without calling live MCP servers, executing tools, modifying external repositories, posting comments, handling tokens, certifying security, guaranteeing quality, proving compliance, or authorizing actions.

ROE-9 adds the first QIRA-Code ReleaseGate pilot receipt packager. It packages a local/offline code-change review into task packet, patch classification, behavior contract, CI evidence summary, reviewer readout, receipt, feedback memory, and gate artifacts without GitHub API calls, external repository mutation, PR comments, merge, deploy, package publish, token handling, correctness proof, security certification, or quality guarantee.

ROE-10 adds the first DataCapsule pilot receipt packager. It packages a local/offline corpus manifest review into source/rights, privacy-risk, evaluation-boundary, use-boundary, reviewer readout, receipt, feedback memory, and gate artifacts without crawling, fetching URLs, inspecting raw private content, uploading data, training models, calling external APIs, token handling, legal/privacy/license/evaluation-cleanliness proof, training authorization, or action authorization.

ROE-11 adds a unified pilot receipt portfolio readout across AgentSec, QIRA-Code ReleaseGate, and DataCapsule. It indexes the three local/offline receipt bundles into a portfolio JSON, vertical comparison matrix, feedback memory index, reviewer readout, claim-boundary sheet, redaction report, and gate result without external APIs, GitHub API calls, live MCP/tool calls, crawling, URL fetching, raw private data inspection, upload, model training, token handling, certification, proof, product-readiness claim, or action authorization.

ROE-12 adds an owner-consented pilot intake kit across AgentSec, QIRA-Code ReleaseGate, and DataCapsule. It creates local intake packets, consent records, vertical routes, redaction preflight, pilot run plans, reviewer instructions, and feedback memory without GitHub API calls, cloning, URL fetching, crawling, live MCP/tool calls, external repo mutation, posting, deploy/release/publish action, upload, model training, token handling, certification, proof, product-readiness claim, or action authorization.

ROE-13 adds the first owner-consented local/sample pilot dry-run. It routes ROE-12 sample intake packets to AgentSec, QIRA-Code ReleaseGate, and DataCapsule, calls only local/offline packager functions, and generates a dry-run trace, vertical results, aggregate receipt, reviewer readout, feedback memory, redaction report, and gate result without external pilots, GitHub API calls, cloning, URL fetching, crawling, live MCP/tool calls, external repo mutation, posting, merge/deploy/publish action, upload, model training, token handling, raw private-data inspection, certification, proof, product-readiness claim, or action authorization.

ROE-14 adds a pilot feedback form and second-run planning gate. It converts local/offline reviewer feedback into feedback packets, deterministic classifications, second-run plans, feedback memory updates, reviewer readout, and gate results without executing second runs by default, calling GitHub APIs, creating issues or comments, cloning, fetching, crawling, running live MCP/tool calls, mutating repositories, posting, merge/deploy/publish action, upload, model training, token handling, private-kernel exposure, certification, proof, product-readiness claim, or action authorization.

ROE-15 adds the first local/sample second-run receipt packager. It reuses ROE-14 feedback and local AgentSec/QIRA/DataCapsule sample receipts to generate updated second-run results, before/after deltas, feedback memory updates, artifact index, reviewer readout, redaction report, and gate result without GitHub APIs, external repositories, posting, merge/deploy/publish action, upload, model training, token handling, unsafe decision upgrades, private-kernel exposure, certification, proof, product-readiness claim, or action authorization.

ROE-16 adds a static/local pilot dashboard artifact pack. It summarizes AgentSec, QIRA, DataCapsule, unified portfolio, intake, dry-run, feedback, and second-run artifacts into JSON, Markdown, HTML, manifest, checksum, redaction, claim-boundary, and gate files without creating a live web app, calling external APIs, adding network dependencies, mutating external repositories, posting, deploy/release/publish action, upload, model training, token handling, private-kernel exposure, certification, proof, product-readiness claim, or action authorization.

ROE-17 adds an external-safe static demo/share pack from the ROE-16 dashboard. It creates a redacted local share folder with README, HTML, Markdown, JSON, claim-boundary, known-limits, operator scripts, manifest, checksums, redaction report, claim audit, distribution boundary, and gate result without deployment, posting, external APIs, network dependencies, live connectors, raw private data, token handling, private-kernel exposure, certification, proof, product-readiness claim, or action authorization.

ROE-18 adds manual-only pilot discovery and feedback intake outreach drafts. It creates reviewer personas, conservative feedback request drafts, a static feedback form template, triage taxonomy, link pack, FAQ, claim boundary, operator checklist, do-not-send guard, redaction report, claim audit, and gate result without sending email, posting, creating issues, calling GitHub or external APIs, scraping, uploading, deploying, token handling, private-kernel exposure, certification, proof, product-readiness claim, or action authorization.

ROE-19 adds local/offline feedback reply packet intake. It converts sample or local reply text into redacted reply packets, classifications, vertical routes, triage entries, feedback memory candidates, second-run candidates, reviewer readout, and gate artifacts without sending replies, creating GitHub issues, posting comments, calling APIs, fetching URLs, mutating repositories, uploading data, training models, token handling, private-kernel exposure, certification, proof, product-readiness claim, or action authorization.

ROE-20 adds a local feedback-to-second-run execution bridge. It selects only `READY_FOR_LOCAL_SECOND_RUN` feedback candidates, executes the ready AgentSec local sample path, and writes skipped reports for HOLD candidates without GitHub APIs, external APIs, issue/comment creation, fetching URLs, live MCP/tool calls, external repository mutation, posting, merge/deploy/publish action, upload, model training, token handling, unsafe decision upgrades, private-kernel exposure, certification, proof, product-readiness claim, or action authorization.

## Quick Example

Example objective request:

```json
{
  "query": "Find a cheap image generation API with commercial-use terms.",
  "domain": "ai_tools",
  "objective": {
    "goal": "select_image_generation_api",
    "must_have": ["commercial_use_terms", "api_access"],
    "nice_to_have": ["free_tier", "clear_rate_limits"]
  },
  "constraints": {
    "max_monthly_budget_usd": 50,
    "requires_documented_terms": true
  },
  "scoring_profile": {
    "weights": {
      "relevance": 0.3,
      "cost_fit": 0.2,
      "policy_clarity": 0.2,
      "documentation_quality": 0.15,
      "source_trace_coverage": 0.15
    }
  },
  "limit": 3
}
```

## Expected Output

An AOI-compatible service should return ranked objects, objective scores, missing fields, warnings, and source trace identifiers. A later read-only MCP tool might produce:

```json
{
  "results": [
    {
      "object_id": "aoi-pixelforge-api",
      "objective_score": 86,
      "rank_reason": "Strong image API relevance, clear commercial-use policy, and low-cost starter tier.",
      "warnings": ["Rate limit details are partially missing."]
    }
  ],
  "source_trace_ids": ["trace-pixelforge-pricing", "trace-pixelforge-terms"]
}
```

## Limitations

- Sample data in this repository is fake but realistic and is intended for contract design, docs, and future evals.
- AOI scores are objective-fit scores, not universal product quality scores.
- Missing fields must be surfaced instead of silently treated as negative or positive proof.
- Source traces can support a field, but they do not guarantee that the source is complete, current, or legally sufficient.
- Freshness is limited by `last_checked_at`, trace retrieval timestamps, and the future ingestion process.

## Package 1 Core Engine Demo

Package 1 adds a local Python core engine over the Package 0 schemas and sample data. It does not add an MCP server, crawler, REST API, supplier verification flow, or any write-capable external action.

After installing the package or running with `src` on `PYTHONPATH`, try:

```powershell
python -m ai_objective_index.cli_demo "cheap image generation API with commercial use terms"
```

The demo loads `data/sample_index.json` and `data/sample_source_traces.json`, searches local sample objects, scores candidates, and prints the top five read-only objective-fit results.

## Package 2 Read-Only MCP Tools

Package 2 exposes the Package 1 core engine as read-only MCP tool functions. If the Python MCP SDK is installed, `ai_objective_index.mcp_server` can register a simple MCP server. If the SDK is missing, the project still works: tool functions and the generated manifest remain available for local tests and integration planning.

Read-only tools:

- `search_objectives`
- `rank_options`
- `compare_tools`
- `explain_score`
- `get_source_trace`
- `list_missing_fields`
- `generate_decision_receipt`

Generate the local manifest:

```powershell
python -m ai_objective_index.mcp_manifest
```

Run the optional server entrypoint:

```powershell
python -m ai_objective_index.mcp_server
```

MCP v0.1 never buys, books, pays, logs in, sends email, submits forms, modifies accounts, claims suppliers, verifies suppliers, or signs contracts.

## Package 3 REST API

Package 3 exposes the same read-only AOI functionality through FastAPI and an OpenAPI spec.

Run locally:

```powershell
python -m ai_objective_index.api
```

Export OpenAPI:

```powershell
python -m ai_objective_index.openapi_export
```

Example search:

```text
GET /search?query=cheap+image+generation+API&objective=low+cost+commercial+use
```

The REST API is read-only. It never buys, books, pays, logs in, sends email, submits forms, modifies accounts, claims suppliers, verifies suppliers, or signs contracts.

## Package 4 Benchmark Reports

Package 4 adds golden query evaluation, benchmark metrics, downloadable JSON files, and Markdown reports.

Run golden query evals:

```powershell
python -m ai_objective_index.eval_runner
```

Generate reports and downloads:

```powershell
python -m ai_objective_index.report_generator
```

Generated report examples:

- `reports/mcp_server_objective_index_v0_1.md`
- `reports/ai_tool_pricing_index_v0_1.md`
- `reports/source_trace_quality_report_v0_1.md`

Package 4 remains read-only. Reports are sample/extracted benchmark artifacts, not quality guarantees, official rankings, legal advice, purchasing advice, or safety certifications.

## Package 5 Hugging Face Demo And Community Testing

Package 5 adds a local Hugging Face demo draft, dataset package, example clients, issue templates, and community launch materials.

Run the local demo:

```powershell
python hf_demo/app.py
```

Publishing to Hugging Face is manual and is not done by this repository automatically. No Hugging Face tokens or external credentials are required.

Feedback loop summary:

- failed queries become golden query candidates;
- wrong fields require official source evidence;
- scoring disputes should name the score component and evidence;
- source trace improvements are prioritized for ranking-relevant fields.

Package 5 remains read-only and does not crawl, buy, book, pay, log in, send email, submit forms, modify accounts, claim suppliers, verify suppliers, or sign contracts.

## Package 6A Crawler / Extractor Skeleton

Package 6A adds a safe crawler/extractor skeleton and a local fixture pipeline. It prepares public-data acquisition mechanics without running broad live crawling.

Preview a crawl plan:

```powershell
python -m ai_objective_index.crawler.crawl_plan
```

Run the local fixture extraction pipeline:

```powershell
python -m ai_objective_index.extractor.fixture_pipeline
```

Package 6A keeps network fetch disabled by default. Tests and demos use local fixtures only. Automatically extracted objects default to `EXTRACTED_UNVERIFIED`, and source traces support fields without becoming quality guarantees.

## Package 6C Generated Extraction Integration

Package 6C integrates the Package 6A generated fixture outputs into explicit local helper flows. Existing API/MCP defaults remain sample-only, while callers can opt into `generated` or `integrated` data scope.

Export integrated index JSON:

```powershell
python -m ai_objective_index.integrated_index_export
```

Run integrated eval:

```powershell
python -m ai_objective_index.integrated_eval
```

Generate integrated report:

```powershell
python -m ai_objective_index.integrated_report_generator
```

Package 6C remains read-only, local-data-only, and no-live-crawling. Generated extracted objects remain `EXTRACTED_UNVERIFIED` and are not verified supplier claims.

## Package 6D-S Source-Governed AOI

Package 6D-S upgrades AOI with source-governance checks before claim promotion. It adds source status, use-right separation, claim ceilings, action-boundary guards, obstruction certificates, AOI decision packets, and false-closure negative controls.

Run false-closure controls:

```powershell
python -m ai_objective_index.negative_control_runner
```

Package 6D-S keeps AOI read-only and local-data-only. A recommendation is not action permission, generated/sample data cannot become verified supplier data, and HOLD/BLOCK certificates must include the next evidence step.

## Package 6D DataScope QA And Beta Readiness

Package 6D hardens `data_scope` behavior across local Core, MCP, REST API, OpenAPI, Hugging Face demo, examples, evals, reports, and docs.

Run data-scope QA:

```powershell
python -m ai_objective_index.datascope_qa
```

Generate beta-readiness report:

```powershell
python -m ai_objective_index.beta_readiness
```

Default scope remains `sample`. Supported scopes are `sample`, `generated`, and `integrated`. Generated records remain `EXTRACTED_UNVERIFIED`. Package 6D performs local readiness checks only; it does not publish, crawl, or execute external actions.

## Package 7A Real MCP SDK Integration And Compatibility Prep

Package 7A adds real MCP runtime hooks and generic read-only `search` / `fetch` wrappers for MCP clients, while reusing the existing AOI MCP/core functions.

Run local MCP smoke:

```powershell
python -m ai_objective_index.mcp_smoke
```

Run the stdio entrypoint:

```powershell
python -m ai_objective_index.mcp_stdio_entrypoint
```

If the optional MCP SDK is missing, the entrypoint prints a safe fallback message. Optional install:

```powershell
pip install "ai-objective-index[mcp]"
```

Package 7A does not submit to an MCP registry automatically and does not enable crawling or external actions.

## Package 7B Public Beta Release Candidate Pack

Package 7B creates a local public beta release candidate pack and readiness audit. It prepares files for manual external release, but it does not publish anything.

Run release readiness:

```powershell
python -m ai_objective_index.release_readiness
```

Run claim audit:

```powershell
python -m ai_objective_index.release_claim_audit
```

Create local release pack:

```powershell
python -m ai_objective_index.public_beta_packager
```

Run all local smoke checks:

```powershell
python -m ai_objective_index.smoke_all
```

The release pack is written to `release/public_beta_v0_1/`. Publishing to GitHub, Hugging Face, MCP Registry, or communities remains manual.

## Package 7C Curated Real-Object Seed Expansion

Package 7C adds a manual curated data path for real-object candidates and an evidence gate for public beta data. Curated objects are not supplier verified and default to `EXTRACTED_UNVERIFIED`.

Run curated export:

```powershell
python -m ai_objective_index.curated_index_export
```

Run curated eval:

```powershell
python -m ai_objective_index.curated_eval
```

Generate curated report:

```powershell
python -m ai_objective_index.curated_report_generator
```

Supported scopes are now `sample`, `generated`, `integrated`, `curated`, and `public_beta`. Default scope remains `sample`. The `public_beta` scope is curated-only by default and returns a warning if no curated object passes the evidence gate. Package 7C does not crawl, scrape, fetch network data, verify suppliers, publish, or execute external actions.

## Package 7D Official MCP Registry Intake Pilot

Package 7D adds an Official MCP Registry intake pilot. Default mode is offline fixture mode; optional live intake requires `--allow-network` and is limited to read-only registry API GET requests.

Run offline fixture export:

```powershell
python -m ai_objective_index.registry_intake.mcp_registry_export --use-fixture
```

Run registry eval:

```powershell
python -m ai_objective_index.registry_intake.mcp_registry_eval
```

Generate registry report:

```powershell
python -m ai_objective_index.registry_intake.mcp_registry_report_generator
```

Package 7D adds `mcp_registry` and `public_beta_mcp` data scopes. Registry objects remain `EXTRACTED_UNVERIFIED`; fixture records do not promote to `public_beta_mcp`. AOI does not scrape arbitrary websites, follow links, certify security, verify suppliers, publish, or execute external actions.

## Package 7E Live Official MCP Registry Intake

Package 7E adds a controlled live registry run wrapper. Default execution uses no network and processes local manual raw data if present.

Run offline/default mode:

```powershell
python -m ai_objective_index.registry_intake.live_registry_run
```

Explicit live mode:

```powershell
python -m ai_objective_index.registry_intake.live_registry_run --allow-network --max-servers 50
```

Live mode is limited to read-only Official MCP Registry API GET requests. It does not scrape arbitrary pages, follow links, fetch GitHub/package/docs pages, use credentials, publish, or certify security. Objects remain `EXTRACTED_UNVERIFIED`.

## Package 7F Registry Candidate Gate

Package 7F builds a calibrated `public_beta_mcp` candidate dataset from saved MCP Registry metadata. Candidates are registry metadata candidates only; they are not verified, security certified, quality guaranteed, action-ready, or purchasing advice.

Build the beta candidate dataset:

```powershell
python -m ai_objective_index.registry_intake.registry_beta_dataset_builder
```

Run the registry quality audit:

```powershell
python -m ai_objective_index.registry_intake.registry_quality_audit
```

Generate the beta report:

```powershell
python -m ai_objective_index.registry_intake.registry_beta_report_generator
```

Package 7F uses local saved registry files only. It does not run live network, scrape websites, follow links, call external LLM APIs, publish, or execute external actions. `public_beta_mcp` remains `EXTRACTED_UNVERIFIED` registry metadata.

## Package 7G Real Registry Payload Activation

Package 7G protects real/manual MCP Registry raw payloads from fixture overwrite and reprocesses saved registry JSON into `mcp_registry` and `public_beta_mcp` outputs.

Activate an existing raw payload:

```powershell
python -m ai_objective_index.registry_intake.real_payload_activation --use-existing-raw
```

Audit payload mode:

```powershell
python -m ai_objective_index.registry_intake.registry_payload_audit
```

Reprocess all registry outputs:

```powershell
python -m ai_objective_index.registry_intake.registry_reprocess_all
```

If a user places `mcp_registry_raw_v0_1.json` at the repository root, activation can copy it into `data/registry/`. No live network is required.

## Package 8A Real-Data Public Beta Final Preflight

Package 8A regenerates public-beta-facing assets from the activated real/manual Official MCP Registry metadata. It prepares a local v0.2 release candidate pack, but it does not publish anything.

Run the real-data claim audit:

```powershell
python -m ai_objective_index.realdata_claim_audit
```

Build the release candidate matrix:

```powershell
python -m ai_objective_index.release_candidate_matrix
```

Run final preflight:

```powershell
python -m ai_objective_index.final_preflight
```

Create the v0.2 local release pack:

```powershell
python -m ai_objective_index.public_beta_realdata_packager
```

`public_beta_mcp` contains source-traced Official MCP Registry metadata candidates. They are not verified, not security certified, not quality guaranteed, not action-ready, and not purchasing advice.

## Package 8B Manual Public Beta Launch Execution Pack

Package 8B creates a local manual launch workspace and archive for public beta v0.2. It prepares drafts and checks, but does not publish anything.

Create launch materials:

```powershell
python -m ai_objective_index.manual_launch_packager
```

Run launch dry-run:

```powershell
python -m ai_objective_index.launch_dry_run
```

Run no-secrets and claim guards:

```powershell
python -m ai_objective_index.no_secrets_audit
python -m ai_objective_index.launch_claim_guard
```

Build the local archive:

```powershell
python -m ai_objective_index.release_archive_builder
```

Outputs are written to `launch/manual_public_beta_v0_2/` and `dist/ai_objective_index_public_beta_v0_2/`. Publishing to GitHub, Hugging Face, MCP Registry, or communities remains manual.

## Package 8C GitHub Staging Upload

Package 8C prepares a private-by-default GitHub staging upload.

Run local upload preparation:

```powershell
python -m ai_objective_index.github_staging
```

If GitHub CLI is installed and authenticated, the helper can create/push `Isometric-Architect/ai-objective-index` as a private staging repository. If GitHub CLI is missing or not authenticated, it does not push and writes manual instructions under `github_upload/`.

No tokens are requested or stored. No force push, remote deletion, Hugging Face upload, community post, MCP Registry submission, crawling, scraping, or external action is performed.

## Package 8D GitHub Private Staging QA

Package 8D verifies the private GitHub staging repository and binds the real GitHub repo URL into local release and launch materials.

```powershell
python -m ai_objective_index.github_post_upload_qa
python -m ai_objective_index.github_link_binder
python -m ai_objective_index.public_switch_preflight
```

The GitHub repository is private staging at `https://github.com/Isometric-Architect/ai-objective-index` unless the owner manually changes visibility. Package 8D does not make the repo public, create a release, upload to Hugging Face, post to communities, submit to MCP Registry, crawl, scrape, or perform external actions.

## Package 8F Hugging Face Manual Upload Bundle

Package 8F creates self-contained manual-upload folders for Hugging Face:

```powershell
python -m ai_objective_index.hf_upload_packager
python -m ai_objective_index.hf_upload_audit
```

Outputs:

- `hf_upload/space/`: Gradio Space bundle with `app.py`, local AOI source, data, reports, and schemas.
- `hf_upload/dataset/`: Dataset bundle with JSONL/JSON data and a Dataset Card.
- `hf_upload/HF_SPACE_UPLOAD_STEPS.md`
- `hf_upload/HF_DATASET_UPLOAD_STEPS.md`
- `hf_upload/HF_FINAL_CHECKLIST.md`

This package does not upload to Hugging Face, use tokens, store secrets, make GitHub public, post to communities, submit to MCP Registry, crawl, scrape, or perform external actions.

## Package 8G Hugging Face Private Upload

Package 8G can prepare and, only when the local Hugging Face CLI/API is already authenticated, upload the Space and Dataset bundles privately:

```powershell
python -m ai_objective_index.hf_auth_check
python -m ai_objective_index.hf_private_upload --dry-run
python -m ai_objective_index.hf_private_upload --execute
python -m ai_objective_index.hf_post_upload_qa
```

Targets:

- Space: `edict-lab/ai-objective-index-demo`
- Dataset: `edict-lab/ai-objective-index-sample`
- Visibility: private
- Space SDK: Gradio

Package 8G never asks for tokens in chat, prints tokens, stores tokens, commits secrets, makes Hugging Face repos public, posts to communities, submits to MCP Registry, crawls, scrapes, or performs external actions. If local HF authentication is missing, it writes safe login and browser-upload fallback instructions.

## Package 8H Private Deployment Sync

Package 8H binds the private GitHub and Hugging Face deployment links into local docs, verifies private deployment status, audits crosslinks, and can push the sync back to the existing private GitHub repo: https://github.com/Isometric-Architect/ai-objective-index

```powershell
python -m ai_objective_index.deployment_link_sync
python -m ai_objective_index.private_deployment_qa
python -m ai_objective_index.hf_github_crosslink_audit
python -m ai_objective_index.deployment_push_sync --dry-run
python -m ai_objective_index.deployment_push_sync --execute
```

Private deployment links:

- GitHub private repo: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space, private: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset, private: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample

Package 8H does not make GitHub or Hugging Face public, create a GitHub release, post to communities, submit to MCP Registry, print/store tokens, force push, crawl, scrape, or execute external actions.

## Package 8I Public Launch Decision Gate

Package 8I prepares a dry-run public launch decision gate and private reviewer path:

```powershell
python -m ai_objective_index.public_launch_gate
python -m ai_objective_index.public_visibility_switch --dry-run
python -m ai_objective_index.public_launch_claim_audit
python -m ai_objective_index.private_reviewer_packager
python -m ai_objective_index.token_revocation_checklist
```

Actual public visibility switch is blocked unless the user later runs `python -m ai_objective_index.public_visibility_switch --execute` and explicitly sets `AOI_PUBLIC_LAUNCH_CONFIRM=YES`. Package 8I does not make anything public by default, post to communities, submit to MCP Registry, create a GitHub Release, print/store tokens, or claim verification, safety, certification, quality guarantee, or purchasing advice.

## Package 8I-R No-Contact Public Beta Gate

Package 8I-R removes any dependency on private reviewers. If no private reviewers are available, AOI can use deterministic local AI/self-review, conservative public wording, and GitHub Issues as the feedback loop:

```powershell
python -m ai_objective_index.ai_reviewer_simulation
python -m ai_objective_index.issue_feedback_loop_packager
python -m ai_objective_index.public_beta_message_guard
python -m ai_objective_index.no_contact_launch_gate
```

This path still does not make anything public by default. It does not post to communities, submit to MCP Registry, call external LLM APIs, print/store tokens, or claim that `public_beta_mcp` candidates are verified, safe, security certified, quality guaranteed, production-ready, or purchasing advice.

## Package 8J Pre-Public Sync And Final Public Dry-Run

Package 8J syncs the latest no-contact beta gate materials to private staging and runs the final public visibility dry-run:

```powershell
python -m ai_objective_index.prepublic_sync --dry-run
python -m ai_objective_index.final_public_dry_run
python -m ai_objective_index.prepublic_state_report
```

If the dry-run is clean and the owner wants to push private staging updates:

```powershell
python -m ai_objective_index.prepublic_sync --execute
```

Package 8J does not make GitHub or Hugging Face public, create a GitHub Release, post to communities, submit to MCP Registry, print/store tokens, force push, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## Package 8K Public Visibility Switch

Package 8K performs the public visibility switch only after explicit confirmation:

```powershell
python -m ai_objective_index.public_launch_execute --dry-run
$env:AOI_PUBLIC_LAUNCH_CONFIRM="YES"
python -m ai_objective_index.public_launch_execute --execute
python -m ai_objective_index.public_url_qa
python -m ai_objective_index.post_public_state_report
```

Package 8K may make the prepared GitHub repo, Hugging Face Space, and Hugging Face Dataset public. It does not create a GitHub Release, post to communities, submit to MCP Registry, crawl, scrape, call external LLM APIs, print/store tokens, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## Package 8L Post-Public Stabilization

Package 8L stabilizes the public deployment after the visibility switch. It verifies public-stage records, activates the GitHub issue feedback loop, writes token revocation guidance, and creates a 72-hour observation plan:

```powershell
python -m ai_objective_index.post_public_stabilization
python -m ai_objective_index.public_issue_loop
python -m ai_objective_index.token_revocation_verify
python -m ai_objective_index.public_observation_plan
```

Public links:

- GitHub: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample

Package 8L does not post to communities, create a GitHub Release, submit to MCP Registry, crawl, scrape, call external LLM APIs, print/store tokens, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## Package 8M Public Ops Baseline

Package 8M establishes the public operations baseline, classifies remaining working-tree changes, prepares GitHub issue labels, and creates a 72-hour observation log:

```powershell
python -m ai_objective_index.public_ops_baseline
python -m ai_objective_index.worktree_hygiene_audit
python -m ai_objective_index.github_issue_labels --dry-run
python -m ai_objective_index.observation_log
python -m ai_objective_index.release_next_decision_gate
```

If GitHub CLI is authenticated and the dry-run is clean, labels can be created or updated with:

```powershell
python -m ai_objective_index.github_issue_labels --execute
```

Package 8M does not post to communities, create a GitHub Release, submit to MCP Registry, delete generated leftovers, force push, print/store tokens, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## Package 8N Public Observation Runner

Package 8N starts the active 72-hour observation workflow and reviews residual worktree changes:

```powershell
python -m ai_objective_index.public_metrics_snapshot
python -m ai_objective_index.public_observation_runner --phase 0h
python -m ai_objective_index.residual_worktree_review
python -m ai_objective_index.observation_decision_gate --phase 0h
```

Outputs are written to `public_ops/observation/` and `public_ops/residual_review/`. Package 8N does not post to communities, create a GitHub Release, submit to MCP Registry, delete residual files, stage all changes, force push, print/store tokens, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## Package 8O Public Beta Launch Wave 1

Package 8O prepares and can execute the first conservative public beta launch wave:

```powershell
python -m ai_objective_index.github_release_manager --dry-run
python -m ai_objective_index.community_launch_manager --dry-run
python -m ai_objective_index.mcp_registry_server_json_builder
python -m ai_objective_index.mcp_registry_submission_gate --dry-run
python -m ai_objective_index.launch_wave1_report
```

The GitHub release manager targets prerelease tag `v0.2.0-public-beta`. MCP Registry submission remains gated and requires `PASS_SUBMIT_READY` plus `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.

Package 8O does not post to HN, Reddit, OpenAI Developer Community, Product Hunt, or MCP communities automatically. It does not claim verified, safe, security-certified, quality-guaranteed, production-ready, or purchasing-advice status.

## Package 8P PyPI / MCP Registry Readiness

Package 8P prepares a PyPI-based MCP Registry path without uploading or submitting:

```powershell
python -m ai_objective_index.package_metadata_audit
python -m ai_objective_index.pypi_publish_readiness
python -m ai_objective_index.mcp_registry_pypi_builder
python -m ai_objective_index.mcp_registry_publish_readiness
python -m ai_objective_index.pypi_upload_instructions
python -m ai_objective_index.community_manual_queue
```

It adds the MCP Registry README marker, prepares `.mcp/server.json` for a future `registryType: pypi` path, and creates manual TestPyPI/PyPI/MCP Registry instructions. Package 8P does not upload to PyPI, submit to MCP Registry, auto-post to communities, broaden token scopes, print/store tokens, or claim verified/safe/security-certified/quality-guaranteed status.

## Package 8Q-A Local Build Readiness

Package 8Q-A checks/installs local packaging tools (`build` and `twine`), builds local wheel/sdist artifacts, runs `twine check`, and runs a local install smoke test where possible:

```powershell
python -m ai_objective_index.local_build_tools --check
python -m ai_objective_index.local_build_tools --install
python -m ai_objective_index.dist_build_runner
python -m ai_objective_index.local_install_smoke
python -m ai_objective_index.pypi_readiness_refresh
```

It does not upload to TestPyPI/PyPI, submit to MCP Registry, ask for tokens, print tokens, or post to communities.

### Package 8Q-A Resumed

After the vNext 9F distribution gate, AOI uses `0.3.0a1` as the first vNext PyPI/TestPyPI build candidate. The resumed local build path applies that version, builds local artifacts, runs `twine check`, runs local install smoke checks, and refreshes PyPI/MCP Registry readiness:

```powershell
python -m ai_objective_index.version_apply_gate --dry-run
python -m ai_objective_index.version_apply_gate --apply 0.3.0a1
python -m ai_objective_index.local_build_tools --check
python -m ai_objective_index.dist_build_runner
python -m ai_objective_index.local_install_smoke
python -m ai_objective_index.pypi_readiness_refresh
python -m ai_objective_index.mcp_registry_readiness_refresh
```

This still does not upload to TestPyPI/PyPI, submit MCP Registry metadata, request tokens, or create `.pypirc`.

### Package 8Q-C-alt Real PyPI Direct Gate

Because TestPyPI signup is blocked for the owner, Package 8Q-C-alt adds a stricter real PyPI direct upload gate for `0.3.0a1`:

```powershell
python -m ai_objective_index.real_pypi_upload_gate
python -m ai_objective_index.real_pypi_upload_runner --dry-run
```

If the gate passes, the owner can run `python -m ai_objective_index.real_pypi_upload_runner --execute` with `AOI_REAL_PYPI_UPLOAD_CONFIRM=YES` and enter the PyPI token only into twine's local prompt. This package does not use TestPyPI, submit MCP Registry metadata, post to communities, create `.pypirc`, print/store tokens, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

### Package 8R MCP Registry Publish Gate

Package 8R prepares the Official MCP Registry path after real PyPI install verification. It validates `.mcp/server.json`, checks `mcp-publisher`, writes a dry-run result, and records post-publish audit helpers:

```powershell
python -m ai_objective_index.mcp_publisher_setup --check
python -m ai_objective_index.mcp_registry_manifest_final_audit
python -m ai_objective_index.mcp_registry_publish_runner --dry-run
```

Actual registry submission remains gated by `mcp-publisher` availability, GitHub authentication, a passing manifest audit, and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`. Registry publication is a metadata listing only; it is not verification, security certification, a quality guarantee, product-readiness evidence, purchasing advice, or action authorization.

### Package 8S Technology Protection

Package 8S hardens the public/private split before increasing discovery through MCP Registry:

```powershell
python -m ai_objective_index.tech_protection_audit
python -m ai_objective_index.public_private_split_audit
python -m ai_objective_index.package_artifact_exposure_audit
python -m ai_objective_index.anti_clone_risk_audit
python -m ai_objective_index.license_ip_positioning_audit
python -m ai_objective_index.mcp_registry_pre_publish_protection_gate
```

Public AOI exposes schemas, read-only API/MCP surfaces, high-level route components, source traces, ALLOW/HOLD/BLOCK labels, limitations, and sample data. Private calibration, exact weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, commercial routing policy, and private data strategy remain non-public. This protection layer does not submit MCP Registry metadata, install `mcp-publisher`, upload a new PyPI version, or claim verification, safety, security certification, quality guarantee, product readiness, purchasing advice, or action authorization.

### Package 8R-B MCP Registry Submit

Package 8R-B is the guarded submit path after PyPI verification and the 8S protection gate:

```powershell
python -m ai_objective_index.mcp_publisher_installer --check
python -m ai_objective_index.mcp_registry_publish_preflight
python -m ai_objective_index.mcp_registry_submit_execute --dry-run
```

Actual Registry publish remains blocked unless `mcp-publisher` is available, GitHub auth is complete, preflight is `PASS_READY_TO_SUBMIT`, and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set. The Registry listing is not verification, security certification, a quality guarantee, product-readiness evidence, purchasing advice, or action authorization.

## Package 9A AOI vNext Alignment

Package 9A pauses the PyPI/MCP Registry publishing path long enough to align AOI vNext around the positioning:

**AI Agent Capability Trust Router**

vNext frames AOI as the trust/routing layer above registries: it routes AI agents from objectives to capabilities with evidence, residual risk, and usage boundaries. It adds ObjectiveCard, CapabilityCard, ExecutionReceipt, ResidualCredit, ProbeCard, and CapabilityGraph schema drafts.

Package 9A is strategy/schema alignment only. It does not upload to PyPI, submit to MCP Registry, post to communities, run probes, execute a security gateway, or claim verification, security certification, quality guarantee, or purchasing advice.

## Package 9B Capability Trust Schema MVP

Package 9B turns the vNext card strategy into a minimal offline capability trust model. It creates `CapabilityTrustCard`, `CapabilityEvidenceSummary`, `ObjectiveCapabilityMatch`, `CapabilityRiskBoundary`, `CapabilityRouteDecision`, `CapabilityTrustProfile`, and `CapabilityTrustReport`.

Run a local trust report:

```powershell
python -m ai_objective_index.vnext.trust_cli --query "find MCP servers for browser automation" --objective "select source-traced MCP candidates" --data-scope public_beta_mcp --limit 5
python -m ai_objective_index.vnext_capability_trust_audit
```

CapabilityTrust is a conservative routing-readiness estimate. It is not a quality guarantee, security certification, supplier verification, purchasing advice, product readiness claim, or action permission. Package 9B does not run probes, execute a gateway, upload to PyPI, submit to MCP Registry, post to communities, crawl, scrape, or call external LLM APIs.

## Package 9C Objective Router API MVP

Package 9C exposes the vNext Capability Trust model through read-only REST and MCP surfaces:

- `POST /v1/objectives/route`
- `POST /v1/objectives/trust-report`
- `GET /v1/capabilities/{capability_id}/trust`
- `GET /v1/objectives/router/status`
- MCP tools: `route_objective`, `get_capability_trust`, `explain_route_decision`

Generate the separate vNext OpenAPI file:

```powershell
python -m ai_objective_index.vnext.objective_router_openapi
```

Run a local Objective Router demo:

```powershell
python -m ai_objective_index.vnext.objective_router_cli_demo --query "browser automation MCP server" --objective "select source-traced MCP candidates" --data-scope public_beta_mcp --limit 5
```

Objective Router returns route decisions, not final truth. It does not run probes, execute tools, fetch live URLs, perform gateway actions, upload packages, submit MCP Registry metadata, or post to communities.

## Package 9D ExecutionReceipt Loop MVP

Package 9D adds a local/offline receipt loop for manual outcomes after a user or agent tries a routed capability:

- `POST /v1/execution-receipts`
- `GET /v1/execution-receipts/{receipt_id}`
- `GET /v1/capabilities/{capability_id}/execution-receipts`
- `GET /v1/capabilities/{capability_id}/receipt-memory`
- `GET /v1/objectives/{objective_id}/receipt-summary`
- `POST /v1/objectives/route-with-receipts`
- `GET /v1/execution-receipts/status`
- MCP tools: `submit_execution_receipt`, `get_execution_receipt`, `list_capability_receipts`, `get_capability_receipt_memory`, `route_objective_with_receipts`

Run the offline demo:

```powershell
python -m ai_objective_index.vnext.execution_receipt_cli_demo
python -m ai_objective_index.vnext_execution_receipt_audit
```

ExecutionReceipt memory can record failures, missing fields, and residual notes. It can add warnings or downgrade routes, but it cannot verify a capability, certify security, guarantee quality, establish product readiness, authorize actions, run probes, execute tools, fetch live URLs, upload packages, submit MCP Registry metadata, or post to communities.

## Package 9E: Probe-before-Use MVP

Package 9E adds a local-only probe-before-use layer on top of the vNext Objective Router. It can plan deterministic metadata probes, run local fixture checks and negative controls, store probe receipts, and overlay probe warnings or downgrades on routes.

New REST endpoints:

- `POST /v1/probes/plan`
- `POST /v1/probes/run-local`
- `GET /v1/probes/{receipt_id}`
- `GET /v1/capabilities/{capability_id}/probe-memory`
- `POST /v1/objectives/route-with-probes`
- `GET /v1/probes/status`

New MCP tools: `plan_probe_before_use`, `run_local_probe_plan`, `get_probe_receipt`, `get_capability_probe_memory`, `route_objective_with_probes`.

Run the offline demo:

```powershell
python -m ai_objective_index.vnext.probe_cli_demo --query "browser automation MCP server" --objective "select source-traced MCP candidates" --data-scope public_beta_mcp --limit 5
python -m ai_objective_index.vnext_probe_audit
```

Probe results are pre-use warnings over local metadata. They do not call live MCP servers, execute external tools, fetch URLs, certify security, guarantee quality, verify capabilities, authorize actions, upload packages, submit registry metadata, or post to communities.

## Package 9F: vNext Distribution Gate

Package 9F audits README, package version, `.mcp/server.json`, OpenAPI, MCP manifest, vNext docs, and claim boundaries before resuming the PyPI/TestPyPI path.

```powershell
python -m ai_objective_index.vnext_surface_sync_audit
python -m ai_objective_index.vnext_package_version_audit
python -m ai_objective_index.residualops_alignment_audit
python -m ai_objective_index.vnext_distribution_gate
python -m ai_objective_index.vnext_pypi_resume_gate
```

The current vNext distribution gate recommends choosing `0.3.0` or `0.3.0a1` before upload-oriented packages. Package 9F itself does not upload to PyPI/TestPyPI, submit MCP Registry metadata, post to communities, execute external tools, call live MCP servers, fetch URLs, or request tokens.

## Claim Boundary

Allowed claim: AOI is a read-only MCP/API objective ranking and comparison tool with explicit schemas, sample source traces, missing-field reporting, and decision receipt contracts.

Forbidden claims: AOI is an official standard, a guarantee of quality, a comprehensive market index, a paid placement system, or a system that automatically purchases, books, pays, emails, logs in, submits forms, or signs contracts.

AOI output is not a quality guarantee. It is not legal, financial, medical, purchasing, compliance, procurement, or professional advice. Humans and downstream agents must verify important decisions against primary sources and current requirements.

## Repository Map

- `schemas/`: JSON Schemas for objective requests, action objects, objective scores, source traces, decision receipts, and read-only MCP tool descriptions.
- `docs/scoring_methodology.md`: v0.1 scoring method and penalties.
- `docs/claim_boundaries.md`: allowed and forbidden claims.
- `docs/productization_mode.md`: how Codex should separate research claim ceilings from productization permission.
- `docs/public_claim_policy.md`: allowed and forbidden public claims.
- `docs/datascope_usage.md`: how to use local AOI data scopes.
- `docs/curated_data_policy.md`: manual curated data policy and public beta scope boundary.
- `docs/curated_evidence_gate.md`: PASS/HOLD/BLOCK evidence gate for curated objects.
- `docs/mcp_registry_intake.md`: Official MCP Registry intake pilot and fallback path.
- `docs/registry_candidate_gate.md`: calibrated `public_beta_mcp` candidate gate.
- `docs/public_beta_mcp_policy.md`: public beta MCP candidate claim boundary.
- `docs/real_registry_payload_activation.md`: manual registry payload activation.
- `docs/anti_fixture_regression_policy.md`: fixture overwrite and promotion guardrails.
- `docs/realdata_public_beta_policy.md`: real-data public beta candidate boundary.
- `docs/package_8a_realdata_public_beta_preflight.md`: final preflight and v0.2 pack commands.
- `docs/package_8b_manual_public_beta_launch.md`: manual public beta launch workspace commands.
- `docs/no_secrets_policy.md`: local no-secrets audit policy.
- `docs/launch_claim_guard.md`: launch claim guard policy.
- `docs/github_staging_upload.md`: private-by-default GitHub staging upload notes.
- `docs/github_post_upload_checklist.md`: manual post-upload review checklist.
- `docs/github_private_staging_review.md`: GitHub private staging review workflow.
- `docs/public_visibility_switch_policy.md`: manual private-to-public switch policy.
- `docs/package_8d_github_private_staging_qa.md`: Package 8D QA and link-binding commands.
- `docs/package_8g_huggingface_private_upload.md`: private Hugging Face CLI/API upload commands and fallback behavior.
- `docs/huggingface_cli_upload.md`: Hugging Face authentication and private upload notes.
- `docs/huggingface_post_upload_checklist.md`: private HF post-upload review checklist.
- `docs/package_8h_private_deployment_sync.md`: private deployment link sync and push commands.
- `docs/private_deployment_review.md`: private GitHub/HF deployment review checklist.
- `docs/hf_github_link_policy.md`: private link wording and claim policy.
- `docs/package_8i_public_launch_decision_gate.md`: public launch dry-run gate and confirmation rule.
- `docs/public_launch_policy.md`: private-to-public policy and claim boundaries.
- `docs/private_reviewer_workflow.md`: private reviewer workflow before public launch.
- `docs/no_contact_public_beta_strategy.md`: no-contact public beta strategy when private reviewers are unavailable.
- `docs/ai_reviewer_simulation.md`: deterministic local reviewer roles.
- `docs/issue_based_feedback_loop.md`: GitHub Issues feedback workflow.
- `docs/package_8j_prepublic_sync.md`: pre-public private sync and dry-run commands.
- `docs/final_public_dry_run.md`: final dry-run and public switch gating.
- `docs/package_8k_public_visibility_switch.md`: explicit public visibility switch gate.
- `docs/post_public_review.md`: post-public URL and claim-boundary review.
- `docs/package_8l_post_public_stabilization.md`: post-public stabilization commands.
- `docs/post_public_observation.md`: 72-hour public observation plan.
- `docs/issue_feedback_after_public.md`: GitHub Issues feedback loop.
- `docs/token_revocation_public_stage.md`: post-public Hugging Face token revocation guidance.
- `docs/package_8m_public_ops_baseline.md`: public operations baseline commands.
- `docs/worktree_hygiene_policy.md`: generated-output and dirty-worktree classification policy.
- `docs/github_issue_loop_operations.md`: public issue loop label and triage workflow.
- `docs/public_metrics_baseline.md`: public beta metrics interpretation.
- `docs/package_8n_public_observation_runner.md`: active 72-hour observation runner commands.
- `docs/public_observation_runner.md`: phase-based public observation workflow.
- `docs/residual_worktree_review_policy.md`: residual working-tree review policy.
- `docs/package_8o_public_beta_launch_wave1.md`: first public beta launch wave commands.
- `docs/github_release_public_beta.md`: GitHub prerelease policy.
- `docs/conservative_community_feedback_launch.md`: conservative feedback launch wording.
- `docs/mcp_registry_submission_gate.md`: MCP Registry eligibility and submission gate.
- `docs/package_8p_mcp_registry_pypi_readiness.md`: PyPI/MCP Registry readiness commands.
- `docs/pypi_publish_readiness.md`: local build and token-safe PyPI readiness.
- `docs/mcp_registry_pypi_path.md`: `registryType: pypi` path and README marker.
- `docs/package_8r_mcp_registry_publish.md`: MCP Registry publisher setup, dry-run, and optional submit gate.
- `docs/mcp_registry_publish_safety.md`: Registry token and claim-boundary safety.
- `docs/mcp_registry_after_publish.md`: Post-publish verification and monitoring.
- `docs/technology_protection_policy.md`: public/private technology protection policy.
- `docs/public_private_split.md`: public/private split table.
- `docs/anti_clone_strategy.md`: anti-clone risk and moat strategy.
- `docs/package_artifact_exposure_policy.md`: wheel/sdist exposure policy.
- `docs/license_ip_positioning.md`: non-legal license/IP positioning notes.
- `docs/mcp_registry_pre_publish_protection.md`: pre-Registry protection gate.
- `docs/package_8r_b_mcp_registry_submit.md`: guarded MCP Registry submit workflow.
- `docs/mcp_publisher_windows_setup.md`: Windows setup notes for `mcp-publisher`.
- `docs/mcp_registry_submit_runbook.md`: step-by-step Registry submit runbook.
- `docs/mcp_registry_failure_recovery.md`: Registry failure recovery notes.
- `docs/community_manual_post_queue.md`: manual community feedback queue.
- `docs/package_8q_a_local_build_and_twine_check.md`: local build/twine check workflow.
- `docs/pypi_beginner_next_steps.md`: beginner TestPyPI/PyPI account and token steps.
- `docs/vnext/aoi_vnext_strategy.md`: AOI vNext strategy and positioning.
- `docs/vnext/capability_trust_router.md`: capability trust router model.
- `docs/vnext/package_9b_capability_trust_schema_mvp.md`: offline capability trust schema MVP.
- `docs/vnext/capability_trust_card.md`: vNext trust card fields.
- `docs/vnext/capability_route_decision.md`: ALLOW/HOLD/BLOCK routing labels.
- `docs/vnext/package_9c_objective_router_api_mvp.md`: vNext REST/MCP Objective Router surface.
- `docs/vnext/objective_router_api.md`: vNext Objective Router REST endpoints.
- `docs/vnext/objective_router_mcp_tools.md`: vNext Objective Router MCP tools.
- `docs/vnext/package_9d_execution_receipt_loop_mvp.md`: local/offline receipt memory loop.
- `docs/vnext/execution_receipt_loop.md`: route -> use -> receipt -> memory -> overlay flow.
- `docs/vnext/package_9e_probe_before_use_mvp.md`: local-only probe-before-use MVP.
- `docs/vnext/probe_before_use.md`: route -> probe plan -> local receipt -> overlay flow.
- `docs/vnext/package_9f_vnext_distribution_gate.md`: vNext distribution gate and version decision.
- `docs/vnext/residualops_alignment.md`: ResidualOps vocabulary alignment without external action authorization.
- `docs/vnext/public_private_ranking_kernel.md`: public/private ranking kernel split.
- `docs/token_revocation_after_upload.md`: token revocation guidance after HF uploads.
- `docs/public_data_intake_policy.md`: public-data intake limits.
- `docs/real_mcp_integration.md`: real MCP SDK integration and fallback behavior.
- `docs/public_beta_release_plan.md`: public beta release-candidate plan and manual boundary.
- `data/`: sample index objects, mock source traces, and golden queries.
- `data/curated/`: manual curated object templates, seed rows, validation, eval, and public beta index outputs.
- `data/registry/`: MCP Registry fixture/raw payloads, mapped objects, traces, validation, eval, and reports.
- `data/fixtures/`: local Package 6A extraction fixtures.
- `data/generated/`: generated fixture extraction outputs.
- `data/negative_controls/`: Package 6D-S false-closure controls and results.
- `evals/`: placeholder for future evaluation harnesses.
- `reports/`: placeholder for future reports.
- `examples/`: placeholder for future client examples.


## Public Deployment

- GitHub repository: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample
- PyPI package: https://pypi.org/project/ai-objective-index/0.3.0a1/
- Current status: public visibility, GitHub prerelease, and PyPI package are live; community posting and MCP Registry submission are still gated/HOLD.
