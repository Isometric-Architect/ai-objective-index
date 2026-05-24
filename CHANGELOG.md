# Changelog

## DataCapsule-1

- Added a local metadata DataCapsule MVP for dataset/corpus use-boundary decisions.
- Added DataCapsule, DataUseBoundary, RiskFlags, sample metadata, local capsule/report generation, docs, claim audit, public outputs, and tests.
- Preserved boundaries: no crawling, no URL fetch, no private data inspection, no external service calls, no token handling, no legal/privacy/license/data-quality/eval-cleanliness certification, and no action authorization.

## AgentSec-3

- Added an opt-in CI artifact bridge for repository-supplied MCP/tool manifests.
- Added a reusable composite action, inactive example workflow, bridge result model, action manifest audit, docs, sample outputs, and tests.
- Preserved boundaries: no active workflow by default, no live MCP call, no external tool execution, no URL fetch, no GitHub API call, no PR comment, no token handling, no public private-kernel details, no security certification, no quality guarantee, no product-readiness claim, and no action authorization.

## AgentSec-2

- Added local multi-manifest intake and policy-profile gate for AgentSec MCP/tool metadata review.
- Added AgentSecPolicyProfile and AgentSecPolicyGateResult models, sample manifest-set outputs, docs, claim audit coverage, and tests.
- Preserved boundaries: no live MCP calls, no external tool execution, no URL fetch, no token handling, no public private-kernel details, no security certification, no quality guarantee, no product-readiness claim, and no action authorization.

## AgentSec-1

- Added a local/offline MCP/tool manifest scanner that emits ToolRiskPacket, AgentSecScanResult, and action-boundary receipt artifacts.
- Added permission, hidden-instruction, namespace, forbidden-action, and unsupported-claim indicators plus sample public outputs, docs, claim audit, and tests.
- Preserved boundaries: no live MCP call, no external tool execution, no URL fetch, no token handling, no security certification, no quality guarantee, no product-readiness claim, and no action authorization.

## QIRA-8

- Added reviewer-facing PR artifact bundle generation for QIRA local review outputs.
- Added Markdown reviewer report, PR comment draft, artifact manifest, bundle result, docs, public sample outputs, and tests.
- Preserved boundaries: no PR comment posting, no GitHub API calls, no command execution, no patch application, no merge/deploy/upload/publish, no token handling, and no certification/readiness claim.

## QIRA-7

- Added an opt-in GitHub CI evidence bridge that converts repository-owned CI status metadata into QIRA CI evidence and review artifacts.
- Added a reusable composite action, non-active example workflow, action manifest audit, docs, sample outputs, and tests.
- Preserved boundaries: no active workflow by default, no GitHub API calls, no QIRA-owned project command execution, no patch application, no merge/deploy/upload/publish, no token handling, and no certification/readiness claim.

## QIRA-6

- Added CI evidence intake for repository-supplied test/static-check result metadata.
- Added validation, packet augmentation, QIRA-6 review output, CLI sample, docs, and tests.
- Preserved boundaries: QIRA does not run tests, call GitHub APIs, inspect live CI, apply patches, merge, deploy, upload, publish, handle tokens, certify security, guarantee quality, or authorize production actions.

## QIRA-5

- Added a local PR diff/changed-file packet generator that emits conservative QIRA task packets.
- Added a QIRA-5 CLI, sample diff, generated packet, review output, docs, and tests.
- Preserved boundaries: no GitHub API calls, no `git` command execution, no patch application, no project command execution, no deploy, no token handling, no external publishing, and no certification/readiness claim.

## QIRA-4

- Added a reusable GitHub Action dry-run wrapper for QIRA local release-gate review.
- Added a non-active sample workflow under `examples/`, QIRA-4 docs, action dry-run outputs, and action manifest audit.
- Preserved boundaries: no auto-enabled workflow, no project command execution, no patch application, no deploy, no token handling, no external publishing, and no certification/readiness claim.

## QIRA-3

- Added local patch path classification for source, tests, docs, config, CI, dependency, generated/data, private/secret, path escape, and unknown paths.
- Added test-command contracts that record project-supplied commands without executing them and conservatively hold or block network, publish, destructive, install, container, browser, login, or unknown command patterns.
- Added QIRA-3 review CLI, public sample outputs, docs, and tests while preserving no-execution/no-deploy/no-token/no-certification boundaries.

## QIRA-2

- Added local QIRA task packet intake for user-supplied JSON packets with task, expected behavior, changed files or patch diff text, local evidence summary, declared claims, and requested action.
- Added a local packet CLI that writes sample packets, intake results, release-gate reports, and next-step notes without applying patches or executing tests.
- Preserved boundaries: no arbitrary external tool execution, no network, no deploy, no token handling, no PyPI/MCP Registry/community action, and no verification, security-certification, quality-guarantee, production-readiness, legal, or action-authorization claim.

## QIRA-1

- Added a local/offline QIRA-Code ReleaseGate MVP with behavior contracts, patch candidates, validator packets, residual ledgers, patch receipts, action licenses, and a sample CLI demo.
- Added QIRA docs, claim-boundary audit, sample release-gate outputs, and tests.
- Preserved boundaries: no arbitrary external tool execution, no deploy, no token handling, no PyPI/MCP Registry/community action, and no verification, security-certification, quality-guarantee, production-readiness, legal, or action-authorization claim.

## ROE-0

- Added the ResidualOps portfolio strategy package for choosing a narrow implementation sequence instead of opening AgentSec, QIRA, and DataCapsule all at once.
- Added QBCPL coding governance, ROE public/private split, AgentSec, QIRA-Code ReleaseGate, and DataCapsule planning docs.
- Added source-intake and protection-gate helpers that use internal QBCPL/ResidualOps material for planning while keeping source bundles, analysis extracts, private kernels, tokens, and action-authorization claims out of public commits.

## Package 8R-B

- Added guarded MCP Publisher install/check, GitHub auth, Registry submit preflight, dry-run/execute, reconcile, and discovery report helpers.
- Added Windows setup, submit runbook, and failure recovery docs for Official MCP Registry publication.
- Preserved boundaries: no Registry publish unless all gates pass and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`, no token printing/storage/commit, no PyPI modification, no community posting, no private-kernel disclosure, and no certification or product-readiness claim.

## Package 8S

- Added technology protection, public/private split, package artifact exposure, anti-clone, license/IP, and MCP Registry pre-publish protection audits.
- Added placeholder-only private kernel inventory template generation and `.gitignore` hardening for private calibration, data, priors, and negative-control paths.
- Preserved boundaries: no MCP Registry submission, no `mcp-publisher` install/execute, no new PyPI upload, no token handling, and no verification, safety, security-certification, quality-guarantee, product-readiness, purchasing-advice, or action-authorization claim.

## Package 8R

- Added MCP Registry publisher setup, manifest final audit, dry-run/login/execute runner, post-publish verification, and release audit.
- Aligned `.mcp/server.json` with the verified real PyPI `0.3.0a1` package while keeping submission gated by `mcp-publisher`, GitHub auth, and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.
- Preserved boundaries: no Registry submission by default, no new PyPI upload, no community posting, no tokens printed/stored/committed, and no verification, safety, security-certification, quality-guarantee, product-readiness, purchasing-advice, or action-authorization claim.

## Package 8Q-C-alt

- Added a real PyPI direct upload gate for `0.3.0a1` because TestPyPI signup is blocked for the owner.
- Added token-safe real PyPI upload runner, real PyPI install verification, real PyPI release audit, and post-PyPI MCP Registry gate.
- Preserved boundaries: no TestPyPI, no MCP Registry submission, no community posting, no `.pypirc`, no token request/printing/storage/commit, no force push, and no verification, safety, security-certification, quality-guarantee, product-readiness, or purchasing-advice claim.

## Package 8Q-A Resumed

- Applied the vNext build candidate decision around `0.3.0a1` for local PyPI/TestPyPI build readiness.
- Added version apply, local build, twine check, local install smoke, PyPI readiness, and MCP Registry readiness refresh outputs under `public_launch/wave9`.
- Preserved no-upload/no-registry/no-token boundaries.

## Package 9E

- Added local-only probe-before-use models, probe plans, probe results, probe receipts, capability probe memory, and route overlays.
- Added deterministic offline metadata probes, fixture negative controls, REST endpoints, MCP tools, CLI demo, schemas, docs, and claim-boundary audit.
- Preserved vNext limits: no live MCP calls, no external tool execution, no URL fetch, no gateway execution, no verification claim, no security certification, no quality guarantee, and no action authorization.

## Package 9F

- Added vNext distribution gate, surface sync audit, package version audit, ResidualOps alignment audit, and PyPI resume gate.
- Aligned `.mcp/server.json`, README, OpenAPI/MCP manifest docs, and vNext distribution docs around conservative AI Agent Capability Trust Router language.
- Kept PyPI/TestPyPI upload, MCP Registry submission, community posting, live MCP calls, external tools, URL fetching, token handling, and action authorization out of scope.

## 0.1.0-package-0

- Added project identity for AI Objective Index (AOI).
- Added v0.1 read-only claim boundaries.
- Added JSON Schemas for objective requests, action objects, objective scores, source traces, decision receipts, and read-only MCP tool descriptions.
- Added fake but realistic sample index objects, mock source traces, and golden queries for the AI tools/APIs/SaaS/MCP vertical.
- Added documentation placeholders for quickstart, MCP usage, API reference, launch notes, reports, evals, and examples.

## 0.1.0-package-1

- Added Python Package 1 Core Engine with Pydantic models, seed loaders, in-memory store, scoring, source trace helpers, missing-field detection, comparison, decision receipt generation, and CLI demo.
- Added pytest coverage for models, seed loading, scoring, source traces, missing fields, comparisons, and decision receipts.
- Preserved v0.1 read-only boundaries: no MCP server, crawler, REST API, payment, booking, login, email, form submission, purchase, contract execution, or supplier claim verification.

## 0.1.0-package-2

- Added read-only MCP tool wrappers for search, ranking, comparison, score explanation, source trace lookup, missing-field listing, and decision receipt generation.
- Added optional MCP server entrypoint with a safe import guard when the MCP Python SDK is unavailable.
- Added generated manifest support for the read-only MCP tool surface.
- Added pytest coverage for MCP tool outputs and manifest structure.
- Preserved Package 2 exclusions: no crawler, REST API, Hugging Face demo, payment, booking, login, email, form submission, purchase, contract execution, account connection, supplier claim, supplier verification, or profile modification.

## 0.1.0-package-3

- Added read-only FastAPI REST API for status, search, object lookup, ranking, comparison, score explanation, source traces, missing fields, decision receipts, and OpenAPI.
- Added Pydantic API request/response models.
- Added OpenAPI export command that writes `api/openapi.json`.
- Added TestClient coverage for REST endpoints and OpenAPI export.
- Preserved Package 3 exclusions: no crawler, Hugging Face demo, payment, booking, login, email, form submission, purchase, contract execution, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-4

- Added golden query eval runner and `data/eval_results.json` generation.
- Added benchmark metrics for source trace coverage, status counts, missing fields, score distribution, pricing clarity, documentation quality, and policy clarity.
- Added Markdown report generation for MCP/server objective index, AI tool pricing index, and source trace quality.
- Added downloadable JSON exports for action objects, source traces, objective scores, and golden queries.
- Added eval documentation files for golden queries, scoring evals, and failure cases.
- Preserved Package 4 exclusions: no Hugging Face demo, crawler, payment, booking, login, email, form submission, purchase, contract execution, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-5

- Added local Hugging Face demo draft with Gradio-optional import-safe `run_demo_query`.
- Added Hugging Face dataset package draft with JSONL exports and dataset card.
- Added REST/MCP example clients and integration notes.
- Added GitHub issue templates for wrong fields, failed queries, new tools, and scoring disputes.
- Added community launch, failure loop, and Hugging Face manual setup docs.
- Preserved Package 5 exclusions: no crawler, payment, booking, login, email, form submission, purchase, contract execution, account connection, supplier claim/verify, profile modification, automatic Hugging Face publishing, or community posting.

## 0.1.0-package-6a

- Added crawler/extractor skeleton with robots policy, rate limiter, optional fetcher, source cache, sitemap parser, GitHub README helpers, and crawl plan preview.
- Added rule-based extractor modules for page classification, HTML text extraction, field extraction, source trace mapping, confidence, and ActionObject building.
- Added local fixture pipeline that generates extracted objects, source traces, and an extraction report under `data/generated/`.
- Added seed examples, local fixture pages, crawler/extractor docs, and pytest coverage.
- Preserved Package 6A exclusions: no broad live crawling, external LLM extraction, payment, booking, login, email, form submission, purchase, contract execution, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-6c

- Added generated extraction loaders for Package 6A output files.
- Added explicit `sample`, `generated`, and `integrated` store helpers.
- Added integrated index export, integrated eval, and integrated Markdown report commands.
- Added optional `data_scope` support to read-only API and MCP helper calls while preserving `sample` defaults.
- Added generated-data status docs and Package 6C integration docs.
- Preserved Package 6C exclusions: no live crawling, network fetch, external LLM API, Hugging Face publishing, community posting, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-6d-s

- Added source-governance modules for source status, promotion decisions, use rights, claim ceilings, action boundaries, obstruction certificates, and AOI decision packets.
- Added false-closure negative controls and CLI runner for HOLD/BLOCK discipline.
- Extended objective scores, decision receipts, MCP outputs, and API status/search responses with source-governed metadata where safe.
- Added docs for source-governed AOI, use-right policy, action-boundary policy, obstruction certificates, and false-closure controls.
- Preserved Package 6D-S exclusions: no live crawling, network fetch, external LLM API, Hugging Face publishing, community posting, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## Documentation

- Added Productization Mode clarification.
- Added research-to-product bridge documentation.
- Added public claim policy separating product-development permission from unsupported external claims.

## 0.1.0-package-6d

- Added data-scope QA runner for `sample`, `generated`, and `integrated` scopes.
- Added conservative beta-readiness Markdown report generation.
- Hardened API `/status`, MCP manifest, Hugging Face demo, examples, and docs around `data_scope`.
- Added Package 6D docs for data-scope usage and beta-readiness checks.
- Preserved Package 6D exclusions: no live crawling, network fetch, external LLM API, Hugging Face publishing, community posting, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-7a

- Added generic read-only MCP compatibility wrappers: `search` and `fetch`.
- Added optional MCP SDK runtime builder and stdio entrypoint with safe fallback when the SDK is missing.
- Added local MCP smoke command and generated smoke result output.
- Updated MCP manifest, schema, docs, examples, and pyproject console scripts.
- Preserved Package 7A exclusions: no live crawling, network fetch, external LLM API, Hugging Face publishing, community posting, registry submission automation, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-7b

- Added local public beta release readiness audit.
- Added public claim audit for public-facing Markdown.
- Added public beta release candidate pack generator with file manifest and checksums.
- Added all-in-one local smoke command.
- Added release plan, manual publish checklist, claim review, smoke matrix, and Package 7B docs.
- Preserved Package 7B exclusions: no GitHub release publishing, Hugging Face publishing, community posting, MCP Registry submission automation, live crawling, network fetch, external LLM API, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-7c

- Added manual curated object templates, curated JSONL seed files, and curated source trace templates.
- Added curated loaders, validator, public beta evidence gate, export, eval, and Markdown report commands.
- Added `curated` and `public_beta` data scopes while preserving `sample` as the default.
- Updated API, MCP helpers, MCP manifest, Hugging Face demo, examples, and docs for curated/public beta scopes.
- Preserved Package 7C exclusions: no live crawling, scraping, network fetch, external LLM API, Hugging Face publishing, community posting, MCP Registry submission, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-7d

- Added Official MCP Registry intake pilot with offline fixture mode and optional explicit `--allow-network` read-only API GET mode.
- Added registry mapper, loader, evidence gate, export, eval, and report generator.
- Added `mcp_registry` and `public_beta_mcp` data scopes while preserving `sample` as the default.
- Added manual download fallback instructions for registry JSON payloads.
- Updated API, MCP helpers, MCP manifest, Hugging Face demo, examples, docs, and beta-readiness probes for registry scopes.
- Preserved Package 7D exclusions: no broad live crawling, arbitrary scraping, link following, external LLM API, Hugging Face publishing, community posting, MCP Registry submission, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-7e

- Added controlled live Official MCP Registry run wrapper with default offline/manual-raw behavior.
- Added registry run receipts, live payload/object validation helpers, live summary output, and manual fallback status output.
- Preserved default no-network behavior and limited explicit live mode to read-only Official MCP Registry API GET requests.
- Added Package 7E docs and tests for offline fallback, manual raw processing, receipts, and validation.
- Preserved Package 7E exclusions: no broad crawling, arbitrary scraping, link following, GitHub/package/docs fetching, external LLM API, publishing, registry submission, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-7f

- Added calibrated MCP Registry beta candidate gate for `public_beta_mcp`.
- Added registry beta dataset builder, quality audit, and beta report generator.
- Updated `public_beta_mcp` to load calibrated registry metadata candidates when available while preserving `EXTRACTED_UNVERIFIED`.
- Added docs for registry candidate gates and public beta MCP claim boundaries.
- Preserved Package 7F exclusions: no live network, broad crawling, arbitrary scraping, link following, external LLM API, publishing, registry submission, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-7g

- Added real/manual MCP Registry raw payload guard and activation commands.
- Added registry payload audit and full offline registry reprocess command.
- Added anti-fixture regression policy so fixture exports do not silently overwrite real/manual raw payloads.
- Updated manual fallback instructions for browser, Windows PowerShell, and macOS/Linux workflows.
- Preserved Package 7G exclusions: no broad crawling, arbitrary scraping, link following, external LLM API, publishing, registry submission, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-8a

- Added real-data public beta final preflight for the activated Official MCP Registry metadata payload.
- Added v0.2 real-data claim audit, release candidate matrix, and public beta real-data packager.
- Added v0.2 release pack generation under `release/public_beta_v0_2/`.
- Added local HF dataset registry candidate exports and v0.2 report generation.
- Preserved Package 8A exclusions: no publishing, additional live network, crawling, scraping, link following, external LLM API, registry submission, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-8b

- Added manual public beta launch workspace generation under `launch/manual_public_beta_v0_2/`.
- Added launch dry-run, no-secrets audit, launch claim guard, and release archive builder.
- Added local archive output under `dist/ai_objective_index_public_beta_v0_2/`.
- Added launch execution, no-secrets, and claim-guard docs.
- Preserved Package 8B exclusions: no publishing, upload, community posting, MCP Registry submission, live network, crawling, scraping, link following, external LLM API, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-8c

- Added GitHub staging upload helper with private-by-default behavior.
- Added git release audit helpers and hardened `.gitignore`.
- Added GitHub staging and post-upload checklist docs.
- Added `github_upload/` summary/manual-command output path.
- Preserved Package 8C exclusions: no token/password capture, force push, remote deletion, public publish unless explicitly configured, Hugging Face upload, community posting, MCP Registry submission, crawling, scraping, link following, external LLM API, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-8d

- Added GitHub private staging QA command and output.
- Added GitHub link binder for README, release, launch, and community docs.
- Added public switch preflight with required manual confirmation.
- Added GitHub web review checklist, public visibility checklist, and Hugging Face HOLD note.
- Preserved Package 8D exclusions: no visibility change, GitHub release creation, Hugging Face upload, community posting, MCP Registry submission, live crawling, arbitrary scraping, link following, external LLM API, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-8f

- Added Hugging Face manual upload packager for `hf_upload/space/` and `hf_upload/dataset/`.
- Added Hugging Face upload audit for required files, no-secrets checks, claim boundaries, cache exclusions, and no network-fetch snippets in the Space app.
- Added beginner-friendly Space, Dataset, and final checklist upload instructions.
- Preserved Package 8F exclusions: no Hugging Face upload, token usage, secret storage, GitHub public switch, community posting, MCP Registry submission, live crawling, network fetch, arbitrary scraping, link following, external LLM API, payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-8g

- Added Hugging Face authentication check with token-safe output.
- Added private-only Hugging Face Space/Dataset upload helper with dry-run default and browser fallback instructions.
- Added Hugging Face post-upload QA for private Space/Dataset URLs.
- Added Package 8G Hugging Face CLI/API upload docs and tests.
- Preserved Package 8G exclusions: no token capture or printing, public Hugging Face visibility, community posting, MCP Registry submission, GitHub public switch, live crawling, scraping, link following, external data fetch beyond HF upload operations, external LLM API, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-8h

- Added private deployment link sync for GitHub, Hugging Face Space, and Hugging Face Dataset URLs.
- Added private deployment QA, HF/GitHub crosslink audit, and private GitHub push sync helper.
- Added private deployment review, link policy, token revocation reminder, and post-deployment checklist assets.
- Preserved Package 8H exclusions: no public visibility switch, GitHub release creation, Hugging Face public switch, community posting, MCP Registry submission, crawling, scraping, link following, external LLM API, token printing/storage, force push, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-8i

- Added public launch decision gate with dry-run default and explicit confirmation requirement.
- Added guarded public visibility switch helper requiring `AOI_PUBLIC_LAUNCH_CONFIRM=YES` for execute mode.
- Added public launch claim audit, private reviewer invite/drafts, GO/NO-GO decision, and token revocation checklist.
- Preserved Package 8I exclusions: no default public switch, community posting, MCP Registry submission, GitHub Release creation, crawling, scraping, link following, external LLM API, token printing/storage, force push, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

## 0.1.0-package-8i-r

- Added no-contact public beta gate for cases where private reviewers are unavailable.
- Added deterministic local AI reviewer simulation across skeptic, developer, agent-user, data-quality, and business-positioning roles.
- Added issue-based feedback loop packaging, conservative public beta message guard, and no-contact GO/NO-GO drafts.
- Preserved Package 8I-R exclusions: no default public switch, community posting, MCP Registry submission, external LLM API calls, crawling, scraping, link following, token printing/storage, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## 0.1.0-package-8j

- Added pre-public private sync helper with dry-run default and selected safe staging paths.
- Added final public visibility dry-run and pre-public state report.
- Added final public switch instructions and pre-public review checklist.
- Preserved Package 8J exclusions: no public visibility change, community posting, MCP Registry submission, GitHub Release creation, crawling, scraping, link following, external LLM API calls, token printing/storage, force push, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## 0.1.0-package-8k

- Added explicit public visibility switch executor requiring `AOI_PUBLIC_LAUNCH_CONFIRM=YES`.
- Added public URL QA and post-public state reporting.
- Added post-public review checklist, community post HOLD note, and token revocation reminder.
- Preserved Package 8K exclusions: no community posting, GitHub Release creation, MCP Registry submission, crawling, scraping, link following, external LLM API calls, token printing/storage, force push, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## 0.1.0-package-8l

- Added post-public stabilization checks for public URLs, claim boundaries, no-secrets status, release HOLD status, and `public_beta_mcp` count.
- Added public GitHub issue loop activation with missing source trace and install failure templates, suggested labels, and first golden query checklist.
- Added Hugging Face token revocation verification guidance and a 72-hour public observation plan.
- Preserved Package 8L exclusions: no community posting, GitHub Release creation, MCP Registry submission, crawling, scraping, link following, external LLM API calls, token printing/storage, force push, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## 0.1.0-package-8m

- Added public operations baseline reporting for GitHub, Hugging Face Space, Hugging Face Dataset, `public_beta_mcp`, and issue-loop readiness.
- Added worktree hygiene audit and Markdown classification for generated leftovers, review-required artifacts, ignore candidates, and do-not-commit files.
- Added GitHub issue label dry-run/execute helper with token-safe output and no label deletion.
- Added 72-hour observation log scaffold and next decision gate.
- Preserved Package 8M exclusions: no community posting, GitHub Release creation, MCP Registry submission, crawling, scraping, link following, external LLM API calls, token printing/storage, force push, file deletion, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## 0.1.0-package-8n

- Added public metrics snapshot and active 72-hour observation runner.
- Added residual worktree review with commit, ignore, and user-review plans.
- Added observation decision gate for `observe_72h`, public URL fixes, claim fixes, and residual worktree cleanup decisions.
- Preserved Package 8N exclusions: no community posting, GitHub Release creation, MCP Registry submission, crawling, scraping, link following, arbitrary external data fetch, external LLM API calls, token printing/storage, force push, generated-leftover deletion, broad staging, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## 0.1.0-package-8o

- Added GitHub public beta prerelease manager for `v0.2.0-public-beta`.
- Added conservative community feedback drafts and optional safe discussion helper.
- Added MCP Registry server JSON draft builder and submission eligibility gate.
- Added launch wave 1 report and post-launch monitoring checklist.
- Preserved Package 8O exclusions: no exaggerated claims, no HN/Reddit/OpenAI/Product Hunt/MCP community auto-posting, no MCP Registry submission unless gated and explicitly confirmed, no crawling, scraping, link following, arbitrary external data fetch, external LLM API calls, token printing/storage, force push, release deletion, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## 0.1.0-package-8p

- Added package metadata audit for PyPI/MCP Registry readiness.
- Added local PyPI build readiness helper with no upload behavior.
- Added PyPI-based `.mcp/server.json` builder and MCP Registry publish readiness gate.
- Added TestPyPI/PyPI/MCP Registry manual upload instructions and community manual post queue.
- Updated package version to `0.2.0` for public beta packaging readiness.
- Preserved Package 8P exclusions: no PyPI/TestPyPI upload, no MCP Registry submission, no HN/Reddit/OpenAI/Product Hunt auto-posting, no Hugging Face permission expansion, no token printing/storage, no crawling, scraping, link following, arbitrary external data fetch, external LLM API calls, force push, GitHub Release deletion, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## 0.1.0-package-8q-a

- Added local build tool checker/installer for `build` and `twine`.
- Added dist build runner for local wheel/sdist creation and `twine check`.
- Added local install smoke helper for built wheel verification.
- Added PyPI readiness refresh result and beginner next-step instructions.
- Preserved Package 8Q-A exclusions: no TestPyPI/PyPI upload, no MCP Registry submission, no token request/printing/storage/commit, no community posting, no external LLM calls, no crawling/scraping/link following, no force push, no GitHub Release deletion, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## 0.1.0-package-9a

- Added AOI vNext strategy docs positioning AOI as an AI Agent Capability Trust Router.
- Added vNext Pydantic model stubs and JSON schema drafts for ObjectiveCard, CapabilityCard, ExecutionReceipt, ResidualCredit, ProbeCard, and CapabilityGraph.
- Added vNext claim-boundary audit and package hold note.
- Paused PyPI/MCP Registry publishing path until vNext alignment is complete.
- Preserved Package 9A exclusions: no PyPI/TestPyPI upload, no MCP Registry submission, no community posting, no claim that AOI is already a security gateway, no claims of verification, safety, security certification, quality guarantee, ecosystem dominance, purchasing advice, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, crawling, scraping, link following, external LLM calls, token printing/storage/commit, or force push.

## 0.1.0-package-9b

- Added vNext Capability Trust Schema MVP with CapabilityTrustCard, CapabilityEvidenceSummary, ObjectiveCapabilityMatch, CapabilityRiskBoundary, CapabilityRouteDecision, CapabilityTrustProfile, and CapabilityTrustReport.
- Added offline trust report CLI for local sample, integrated, MCP Registry, and public beta MCP scopes.
- Added deterministic ALLOW/HOLD/BLOCK route-decision rules and claim-boundary audit for capability trust artifacts.
- Added vNext JSON schema drafts and Package 9B documentation.
- Preserved Package 9B exclusions: no probe execution, gateway execution, live security scanning, crawling, scraping, link following, external LLM calls, PyPI/TestPyPI upload, MCP Registry submission, community posting, token printing/storage/commit, force push, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, product readiness, or purchasing advice.

## 0.1.0-package-9c

- Added vNext Objective Router request/response models and read-only route service.
- Added REST endpoints for objective routing, trust reports, capability trust cards, and router status.
- Added MCP tools `route_objective`, `get_capability_trust`, and `explain_route_decision`.
- Added separate vNext Objective Router OpenAPI export, examples, CLI demo, and claim-boundary audit.
- Preserved Package 9C exclusions: no probe execution, gateway execution, external tool execution, live URL fetch, crawling, scraping, link following, external LLM calls, PyPI/TestPyPI upload, MCP Registry submission, community posting, token printing/storage/commit, force push, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, or claims of verification, safety, security certification, quality guarantee, product readiness, or purchasing advice.

## 0.1.0-package-9d

- Added local/offline ExecutionReceipt submission, validation, storage, capability memory, objective summary, and route overlay models.
- Added REST endpoints for execution receipts, receipt memory, objective receipt summaries, route-with-receipts, and receipt loop status.
- Added MCP receipt-memory tools and regenerated the MCP manifest surface.
- Added offline CLI demo, vNext schemas, API examples, docs, and receipt claim-boundary audit.
- Preserved Package 9D exclusions: no external tool execution, probe execution, gateway execution, live URL fetch, crawling, scraping, link following, external LLM calls, PyPI/TestPyPI upload, MCP Registry submission, community posting, token printing/storage/commit, payment, booking, login automation, email, form submission, purchase, contract signing, account connection, supplier claim/verify, profile modification, action authorization, or claims of verification, safety, security certification, quality guarantee, product readiness, or purchasing advice.
