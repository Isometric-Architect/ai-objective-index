# Package 8K Public Visibility Switch

Package 8K performs the public visibility switch only after explicit confirmation.

It may make the prepared GitHub repository, Hugging Face Space, and Hugging Face Dataset public. It does not create a GitHub Release, post to communities, submit to MCP Registry, crawl, scrape, follow links, call external LLM APIs, print/store tokens, force push, or execute external actions.

## Required Confirmation

Execute mode requires:

```powershell
$env:AOI_PUBLIC_LAUNCH_CONFIRM="YES"
python -m ai_objective_index.public_launch_execute --execute
```

Without that environment variable, the command refuses to change visibility.

## Dry-Run

```powershell
python -m ai_objective_index.public_launch_execute --dry-run
```

## Post-Switch QA

```powershell
python -m ai_objective_index.public_url_qa
python -m ai_objective_index.post_public_state_report
```

## Boundaries

Public visibility does not mean AOI is verified, safe, security certified, quality guaranteed, production-ready, purchasing advice, or action-ready. `public_beta_mcp` remains a source-traced registry metadata candidate dataset.
