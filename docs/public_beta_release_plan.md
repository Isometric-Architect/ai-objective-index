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

## Package 8D GitHub Private Staging QA

Package 8D verifies the private GitHub staging repository, binds `https://github.com/Isometric-Architect/ai-objective-index` into local release materials, and prepares a manual public-switch checklist.

```powershell
python -m ai_objective_index.github_post_upload_qa
python -m ai_objective_index.github_link_binder
python -m ai_objective_index.public_switch_preflight
```

It does not change repository visibility, create a GitHub release, upload to Hugging Face, post to communities, or submit to MCP Registry.

No tokens, credentials, live crawling, network fetch, external LLM calls, payment, booking, login, email, form submission, purchase, account connection, registry submission, Hugging Face publishing, community posting, supplier verification, or contract signing are performed by Package 7B.

## Package 8H Private Deployment Sync

The current deployment links are private review links:

- GitHub private repo: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space, private: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset, private: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample

Run `python -m ai_objective_index.private_deployment_qa` and `python -m ai_objective_index.hf_github_crosslink_audit` before any manual public switch.

## Package 8I Public Launch Decision Gate

Before a public switch, run:

```powershell
python -m ai_objective_index.public_launch_gate
python -m ai_objective_index.public_visibility_switch --dry-run
python -m ai_objective_index.public_launch_claim_audit
python -m ai_objective_index.private_reviewer_packager
python -m ai_objective_index.token_revocation_checklist
```

Actual execute mode requires `AOI_PUBLIC_LAUNCH_CONFIRM=YES`. A PASS result means the user may decide whether to switch public; it is not a product-readiness, security, certification, quality, legal, or purchasing claim.

## Package 8I-R No-Contact Public Beta

Private reviewers are optional, not mandatory. If no private reviewers are available, use:

```powershell
python -m ai_objective_index.ai_reviewer_simulation
python -m ai_objective_index.issue_feedback_loop_packager
python -m ai_objective_index.public_beta_message_guard
python -m ai_objective_index.no_contact_launch_gate
```

This path uses deterministic local checks and GitHub Issues instead of personal outreach. It does not make anything public by default, post to communities, submit to MCP Registry, call external LLM APIs, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## Package 8J Pre-Public Sync

Before any public switch, run the final sync and dry-run:

```powershell
python -m ai_objective_index.prepublic_sync --dry-run
python -m ai_objective_index.final_public_dry_run
python -m ai_objective_index.prepublic_state_report
```

If private staging needs the latest no-contact files, run:

```powershell
python -m ai_objective_index.prepublic_sync --execute
```

Package 8J still does not change visibility. Public switching remains a later manual decision guarded by `AOI_PUBLIC_LAUNCH_CONFIRM=YES`.

## Package 8K Public Visibility Switch

When the owner explicitly approves public visibility:

```powershell
python -m ai_objective_index.public_launch_execute --dry-run
$env:AOI_PUBLIC_LAUNCH_CONFIRM="YES"
python -m ai_objective_index.public_launch_execute --execute
python -m ai_objective_index.public_url_qa
python -m ai_objective_index.post_public_state_report
```

Package 8K changes visibility only. It does not create a GitHub Release, post to communities, submit to MCP Registry, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## Package 8L Post-Public Stabilization

After public visibility is on, run:

```powershell
python -m ai_objective_index.post_public_stabilization
python -m ai_objective_index.public_issue_loop
python -m ai_objective_index.token_revocation_verify
python -m ai_objective_index.public_observation_plan
```

Package 8L activates issue-based feedback and a 72-hour observation plan. It still does not post to communities, create a GitHub Release, submit to MCP Registry, revoke tokens automatically, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.

## Package 8M Public Ops Baseline

After issue-loop activation, run:

```powershell
python -m ai_objective_index.public_ops_baseline
python -m ai_objective_index.worktree_hygiene_audit
python -m ai_objective_index.github_issue_labels --dry-run
python -m ai_objective_index.observation_log
python -m ai_objective_index.release_next_decision_gate
```

Package 8M classifies generated leftovers and prepares public issue labels. The default recommendation remains `observe_72h`. It does not post to communities, create a GitHub Release, submit to MCP Registry, delete generated files, or claim verification, safety, security certification, quality guarantee, production readiness, or purchasing advice.


## Public Deployment

- GitHub repository: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample

## Package 8O Wave 1 Launch

Package 8O can create the `v0.2.0-public-beta` GitHub prerelease and conservative feedback drafts. MCP Registry submission remains gated and should HOLD unless server JSON, package/remote endpoint, publisher tooling, authentication, and explicit confirmation are all present.

Package 8P prepares the PyPI-based MCP Registry path. It can build local package artifacts and write upload instructions, but it does not upload to PyPI or submit to MCP Registry.
- Community posting, GitHub Release creation, and MCP Registry submission remain HOLD.
