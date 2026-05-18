# Package 8B: Manual Public Beta Launch Execution Pack

Package 8B creates a local manual launch execution workspace for AOI public beta v0.2.

It prepares release drafts, Hugging Face upload guides, community post drafts, no-secrets checks, claim guards, dry-run results, and a local archive. It does not publish anything.

## Commands

```powershell
python -m ai_objective_index.manual_launch_packager
python -m ai_objective_index.launch_dry_run
python -m ai_objective_index.no_secrets_audit
python -m ai_objective_index.launch_claim_guard
python -m ai_objective_index.release_archive_builder
```

## Outputs

- `launch/manual_public_beta_v0_2/`
- `dist/ai_objective_index_public_beta_v0_2/`
- `data/generated/launch_dry_run_result_v0_2.json`
- `data/generated/no_secrets_audit_result_v0_2.json`
- `data/generated/launch_claim_guard_result_v0_2.json`
- `data/generated/launch_archive_manifest_v0_2.json`

## Boundary

Package 8B is read-only and local-data-only. It does not publish to GitHub, upload to Hugging Face, post to communities, submit to MCP Registry, run live network, crawl, scrape, follow links, call external LLM APIs, or execute payment, booking, login, email, form submission, purchase, account connection, supplier verification, or contract signing.
