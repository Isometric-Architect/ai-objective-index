# Package 8A: Real-Data Public Beta Final Preflight

Package 8A regenerates and verifies public-beta-facing assets using the local real/manual Official MCP Registry payload.

It prepares a local v0.2 public beta release candidate pack, but it does not publish anything.

## Commands

```powershell
python -m ai_objective_index.realdata_claim_audit
python -m ai_objective_index.release_candidate_matrix
python -m ai_objective_index.final_preflight
python -m ai_objective_index.public_beta_realdata_packager
```

## What It Checks

- `mcp_registry` object count is greater than zero.
- `public_beta_mcp` candidate count is greater than zero.
- Active raw payload mode is `manual_raw` or `live_raw`.
- Fixture leakage is false.
- OpenAPI and MCP manifest are present.
- Claim boundaries are not violated in public-facing docs.
- No publish action is performed.

## Boundary

`public_beta_mcp` contains Official MCP Registry metadata candidates. They are not verified, not security certified, not quality guaranteed, not purchasing advice, and not action-ready.

Package 8A does not run live network, crawl, scrape, follow links, fetch repositories/docs/package pages, call external LLM APIs, publish, post, submit to MCP Registry, buy, book, log in, send email, submit forms, purchase, verify suppliers, or sign contracts.
