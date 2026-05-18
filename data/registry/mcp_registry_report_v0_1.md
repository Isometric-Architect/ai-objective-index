# MCP Registry Intake Report v0.1

Generated at: `2026-05-18T10:25:43.791999+00:00`

## What This Report Is

This report summarizes AOI Package 7D intake of Official MCP Registry-style metadata into local read-only AOI records.

## Data Source

- Source mode: `official_mcp_registry_api`
- Default execution is offline fixture mode.

## Scope

- Object type: `MCPServer`
- Status: `EXTRACTED_UNVERIFIED`
- No live crawling / no scraping.

## Object Counts

- Registry object count: `50`
- Source trace count: `191`
- Public beta ready count: `0`

## Evidence Gate Summary

- Pass count: `0`
- Hold count: `50`
- Block count: `0`
- Token counts: `{"HOLD_MISSING_REPO": 22, "HOLD_MISSING_DOCS": 28}`

## Top Example Objects

- `mcp-registry-ac-tandem-docs-mcp-0-3-0` - ac.tandem/docs-mcp (`EXTRACTED_UNVERIFIED`)
- `mcp-registry-ac-tandem-docs-mcp-0-3-1` - ac.tandem/docs-mcp (`EXTRACTED_UNVERIFIED`)
- `mcp-registry-ac-tandem-docs-mcp-0-3-2` - ac.tandem/docs-mcp (`EXTRACTED_UNVERIFIED`)
- `mcp-registry-agency-lona-trading-2-0-0` - agency.lona/trading (`EXTRACTED_UNVERIFIED`)
- `mcp-registry-ai-abmeter-abmeter-0-1-0` - ai.abmeter/abmeter (`EXTRACTED_UNVERIFIED`)

## Missing Fields Summary

- Missing field counts: `{'pricing': 50, 'free_plan': 50, 'commercial_use_terms': 50, 'rate_limits': 50, 'privacy_policy': 50, 'docs_url': 50, 'refund_policy': 50, 'data_retention_policy': 50, 'repository_or_homepage': 22, 'clear_capabilities': 45}`

## Limitations

- Registry metadata is not supplier verified by AOI.
- AOI does not claim the servers are safe, secure, maintained, or high quality.
- This is not a security certification.
- Source traces support fields but do not prove completeness or currentness.
- Fixture mode records are not promoted to `public_beta_mcp`.
- No live crawling / no scraping.

## Not Implemented

- broad crawling
- arbitrary website scraping
- link following
- external LLM calls
- payment, booking, login, email sending, form submission, purchase, account connection, supplier verification, or contract signing
