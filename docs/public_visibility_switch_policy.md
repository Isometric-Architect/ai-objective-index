# Public Visibility Switch Policy

Switching the GitHub repository from private to public is a manual owner decision.

Package 8D can prepare a local preflight result, but it must not change visibility automatically.

## Before Public

Run:

```powershell
python -m pytest
python -m ai_objective_index.smoke_all
python -m ai_objective_index.no_secrets_audit
python -m ai_objective_index.launch_claim_guard
python -m ai_objective_index.public_switch_preflight
```

Then review GitHub in the browser.

## Claim Boundary

Public visibility does not make AOI production-ready, verified, security certified, quality guaranteed, official, or suitable as purchasing advice.

`public_beta_mcp` contains source-traced Official MCP Registry metadata candidates. They remain not verified, not security certified, not quality guaranteed, and not action-ready.

