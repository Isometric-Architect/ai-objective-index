# Final Public Switch Instructions

Package 8J does not make anything public.

## A. Codex-Assisted Public Switch Later

Only after the user explicitly says to proceed:

1. Set `AOI_PUBLIC_LAUNCH_CONFIRM=YES`.
2. Run:

```powershell
python -m ai_objective_index.public_launch_execute --execute
```

Then run:

```powershell
python -m ai_objective_index.public_url_qa
python -m ai_objective_index.post_public_state_report
```

## B. Manual Public Switch

GitHub:

1. Open repository settings.
2. Go to Danger Zone.
3. Change visibility to Public.

Hugging Face Space:

1. Open Space settings.
2. Change Visibility to Public.

Hugging Face Dataset:

1. Open Dataset settings.
2. Change Visibility to Public.

## Warnings

- Do not claim verified MCP servers.
- Do not claim safe servers, security certification, quality guarantee, or production readiness.
- Do not post community announcements until links are public and checked.
