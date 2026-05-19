# Post-Public Observation

The first public hours should be quiet, measured, and evidence-driven.

## First 1 Hour

- Open GitHub, Hugging Face Space, and Hugging Face Dataset public links.
- Test `browser automation MCP server`.
- Confirm source traces and limitations are visible.
- Confirm public wording says not verified, not security certified, not a quality guarantee, and read-only.

## First 24 Hours

- Watch GitHub issues, stars, and clone signals if visible.
- Watch Hugging Face Space runs, likes, or downloads if visible.
- Collect failed queries and confusing docs reports.

## First 72 Hours

- Patch only clear bugs.
- Add useful failures to golden queries.
- Do not overreact to low early attention.
- Do not post community announcements until the public URLs and issue loop are stable.

No immediate attention does not mean failure.

## Package 8M Baseline Commands

```powershell
python -m ai_objective_index.public_ops_baseline
python -m ai_objective_index.observation_log
python -m ai_objective_index.release_next_decision_gate
```

The default next decision is `observe_72h` unless public URL QA, claim audits, or worktree hygiene indicate a fix is needed.
