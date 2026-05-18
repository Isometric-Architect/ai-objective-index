# Manual Launch Execution

AOI launch execution is human-only.

## Required Local Checks

1. `python -m pytest`
2. `python -m ai_objective_index.smoke_all`
3. `python -m ai_objective_index.final_preflight`
4. `python -m ai_objective_index.realdata_claim_audit`
5. `python -m ai_objective_index.manual_launch_packager`
6. `python -m ai_objective_index.no_secrets_audit`
7. `python -m ai_objective_index.launch_claim_guard`
8. `python -m ai_objective_index.release_archive_builder`

## Manual Steps

- Create a GitHub release manually if desired.
- Create a Hugging Face Space manually if desired.
- Create a Hugging Face Dataset manually if desired.
- Post community feedback request manually if desired.
- Submit MCP registry materials manually if desired.

No tokens should be committed to the repository. No automated public release is performed by AOI.
