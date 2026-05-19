# Final Public Dry-Run

`python -m ai_objective_index.final_public_dry_run` checks whether AOI is ready for a later manual public visibility decision.

The command does not change visibility.

## Checks

- no-contact launch gate
- AI reviewer simulation
- public beta message guard
- no-secrets audit
- launch claim guard
- smoke test result
- GitHub remote
- Hugging Face Space status if known
- Hugging Face Dataset status if known
- `public_beta_mcp` candidate count

## Output

The command writes `public_launch/FINAL_PUBLIC_DRY_RUN_RESULT.json`.

The output includes:

- `would_switch.github_repo`
- `would_switch.hf_space`
- `would_switch.hf_dataset`
- `actual_switch_performed=false`
- `required_user_confirmation=true`
- `required_env_for_execute=AOI_PUBLIC_LAUNCH_CONFIRM=YES`

## Meaning

PASS means the owner may decide whether to keep private, pause, or explicitly authorize a public switch later. It does not mean AOI is verified, safe, security certified, quality guaranteed, production-ready, or purchasing advice.
