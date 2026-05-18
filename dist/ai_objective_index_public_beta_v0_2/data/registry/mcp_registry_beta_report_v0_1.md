# MCP Registry Beta Candidate Report v0.1

Generated at: `2026-05-18T10:25:34.445314+00:00`

## What This Report Is

This report summarizes the calibrated `public_beta_mcp` candidate set built from local Official MCP Registry metadata already saved in this repository.

This report is not a security certification, supplier verification, quality guarantee, purchasing advice, or action permission.

## Data Source: Official MCP Registry Metadata

- Source mode: `fixture`
- No live network, scraping, or link following is performed by this report generator.
- Objects remain `EXTRACTED_UNVERIFIED`.

## Candidate Gate Definition

- `PASS_PUBLIC_BETA_CANDIDATE` means the record can appear as registry metadata in beta surfaces.
- It does not mean `VERIFIED`, `ACTION_READY`, safe, secure, maintained, or high quality.
- Missing pricing or policy fields are warnings/HOLD context for MCP registry metadata, not automatic blocks.

## Candidate Count

- Registry objects: `5`
- Source traces: `25`
- Public beta MCP candidates: `0`

## Not Verified / Not Security Certified

- `verified=false` for all candidates.
- `action_ready=false` for all candidates.
- `not_security_certified=true` for the dataset.
- Registry metadata is not supplier verified.

## Top Example Beta Candidates

- No beta candidates are available from the current local registry files.

## Missing Fields

- Missing field stats: `{'total_missing_fields': 35, 'unique_missing_fields': 7, 'objects_with_missing_fields_count': 5, 'by_field': {'pricing': 5, 'free_plan': 5, 'commercial_use_terms': 5, 'rate_limits': 5, 'privacy_policy': 5, 'refund_policy': 5, 'data_retention_policy': 5}, 'objects_with_missing_fields': [{'object_id': 'mcp-registry-io-github-example-browser-automation-0-1-0', 'name': 'io.github.example/browser-automation', 'missing_fields': ['pricing', 'free_plan', 'commercial_use_terms', 'rate_limits', 'privacy_policy', 'refund_policy', 'data_retention_policy'], 'missing_count': 7}, {'object_id': 'mcp-registry-io-github-example-web-search-0-1-0', 'name': 'io.github.example/web-search', 'missing_fields': ['pricing', 'free_plan', 'commercial_use_terms', 'rate_limits', 'privacy_policy', 'refund_policy', 'data_retention_policy'], 'missing_count': 7}, {'object_id': 'mcp-registry-io-github-example-document-extract-0-1-0', 'name': 'io.github.example/document-extract', 'missing_fields': ['pricing', 'free_plan', 'commercial_use_terms', 'rate_limits', 'privacy_policy', 'refund_policy', 'data_retention_policy'], 'missing_count': 7}, {'object_id': 'mcp-registry-io-github-example-vector-db-0-1-0', 'name': 'io.github.example/vector-db', 'missing_fields': ['pricing', 'free_plan', 'commercial_use_terms', 'rate_limits', 'privacy_policy', 'refund_policy', 'data_retention_policy'], 'missing_count': 7}, {'object_id': 'mcp-registry-io-github-example-code-runner-0-1-0', 'name': 'io.github.example/code-runner', 'missing_fields': ['pricing', 'free_plan', 'commercial_use_terms', 'rate_limits', 'privacy_policy', 'refund_policy', 'data_retention_policy'], 'missing_count': 7}]}`

## Quality Audit Summary

- Source trace coverage: `1.0`
- Objects with repositories: `5`
- Objects with packages: `5`
- Hold counts: `{'HOLD_FIXTURE_ONLY': 5}`
- Block counts: `{}`

## How To Use `data_scope=public_beta_mcp`

Use the REST API, MCP tools, or HF demo with `data_scope=public_beta_mcp`. If no candidate rows are available, the surfaces return a warning rather than falling back to fake sample records.

## Limitations

- Registry metadata may be incomplete or stale.
- AOI does not fetch repository, package, docs, or security pages in Package 7F.
- Source traces support registry metadata fields but do not prove currentness or correctness.
- Missing pricing and policy fields are common for MCP registry records.

## Not Implemented

- live network
- broad crawling
- arbitrary scraping
- link following
- external LLM calls
- supplier verification
- security certification
- payment, booking, login, email, form submission, purchase, account connection, or contract signing
