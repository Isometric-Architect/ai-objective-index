# Public Beta Release Plan

Public beta means AOI is packaged for external testers to run locally and review. It is not a general consumer release, certification, marketplace listing, or official standard.

Target audience:

- AI developers;
- MCP users;
- benchmark testers;
- tool-ranking and source-trace reviewers.

Package 7B creates a local release candidate pack only. Publishing remains manual.

The public beta should ask users to test and break golden queries, missing-field behavior, source trace coverage, data scopes, MCP compatibility, REST/OpenAPI surfaces, and public claim boundaries.

Before public beta distribution, either add manually curated real-object rows with source traces or clearly accept that no curated public beta records are ready yet. The `public_beta` data scope is curated-only by default and does not fall back to fake sample records.

For MCP-specific beta candidates, `public_beta_mcp` can be used if Official MCP Registry intake succeeds and records pass the calibrated Package 7F candidate gate. In offline fixture mode, `public_beta_mcp` may be empty. Do not claim registry metadata is supplier verification, security certification, quality guarantee, purchasing advice, or action permission.

Package 7E can attempt a controlled live Official MCP Registry API run only with explicit `--allow-network`. If live access is unavailable, use the manual raw JSON fallback and keep the same claim boundaries.

Before public beta, run `registry_beta_dataset_builder`, `registry_quality_audit`, and `registry_beta_report_generator`, then review candidate counts and not-verified language.

Package 7G adds one more release gate: run `real_payload_activation --use-existing-raw`, `registry_payload_audit`, and `registry_reprocess_all`. If claiming MCP public beta data, require `real_payload_available=true`, `fixture_leak_detected=false`, and `public_beta_mcp_count > 0`.

## v0.2 Real-Data Release Candidate

Package 8A creates a v0.2 local release candidate pack using the activated Official MCP Registry metadata candidates.

Required commands:

```powershell
python -m ai_objective_index.realdata_claim_audit
python -m ai_objective_index.release_candidate_matrix
python -m ai_objective_index.final_preflight
python -m ai_objective_index.public_beta_realdata_packager
```

The v0.2 pack is still manual-publish only. It must describe `public_beta_mcp` as registry metadata candidates, not verified MCP servers, security certified tools, or quality guaranteed tools.

## Package 8B Manual Launch Workspace

Package 8B adds `launch/manual_public_beta_v0_2/` and `dist/ai_objective_index_public_beta_v0_2/` for manual launch execution.

Run:

```powershell
python -m ai_objective_index.manual_launch_packager
python -m ai_objective_index.launch_dry_run
python -m ai_objective_index.no_secrets_audit
python -m ai_objective_index.launch_claim_guard
python -m ai_objective_index.release_archive_builder
```

These commands prepare local files only. They do not publish, upload, submit, post, crawl, scrape, or call external services.

## Package 8C GitHub Staging

Package 8C can prepare a private GitHub staging upload with:

```powershell
python -m ai_objective_index.github_staging
```

If GitHub CLI is unavailable or unauthenticated, it writes manual commands under `github_upload/` and does not push. No token storage, force push, remote deletion, public publish, Hugging Face upload, community posting, or MCP Registry submission is performed.

No tokens, credentials, live crawling, network fetch, external LLM calls, payment, booking, login, email, form submission, purchase, account connection, registry submission, Hugging Face publishing, community posting, supplier verification, or contract signing are performed by Package 7B.
