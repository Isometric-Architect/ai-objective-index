# Package 9E: Probe-before-Use MVP

Package 9E adds a local-only probe-before-use layer for AOI vNext. It creates probe plans, runs deterministic metadata and fixture checks against local AOI records, emits probe receipts, and overlays those receipts onto Objective Router responses.

This package does not execute tools, call live MCP servers, fetch URLs, run crawlers, call external LLMs, upload packages, submit MCP Registry entries, or post to communities.

## Commands

```powershell
python -m ai_objective_index.vnext.probe_cli_demo --query "browser automation MCP server" --objective "select source-traced MCP candidates" --data-scope public_beta_mcp --limit 5
python -m ai_objective_index.vnext_probe_audit
python -m ai_objective_index.no_secrets_audit
python -m ai_objective_index.launch_claim_guard
```

## Claim Boundary

Probe results are pre-use warnings over local metadata. `PASS_LOCAL` does not mean verified, safe, security certified, quality guaranteed, product ready, externally validated, or action authorized.
