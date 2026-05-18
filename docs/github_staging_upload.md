# GitHub Staging Upload

Package 8C prepares AOI for a GitHub staging upload.

## Defaults

- Owner: `Isometric-Architect`
- Repository: `ai-objective-index`
- Visibility: private by default
- Branch: `main`

Public release is manual. To request public creation through automation, set `AOI_GITHUB_VISIBILITY=public` explicitly.

## Requirements

The upload helper can use GitHub CLI if it is installed and authenticated:

```powershell
gh --version
gh auth status
```

If GitHub CLI is missing or not authenticated, AOI does not ask for tokens and does not push. It writes manual fallback commands under `github_upload/`.

## Safety Rules

- No tokens or passwords are requested, printed, or stored.
- No force push.
- No remote repository deletion.
- No overwrite of an existing mismatched remote.
- Default staging repository is private.
- Public release is a separate manual decision.

Before push, run:

```powershell
python -m pytest
python -m ai_objective_index.no_secrets_audit
python -m ai_objective_index.launch_claim_guard
python -m ai_objective_index.smoke_all
```

AOI remains a read-only MCP/API benchmark. `public_beta_mcp` contains registry metadata candidates, not verified or security certified tools.
