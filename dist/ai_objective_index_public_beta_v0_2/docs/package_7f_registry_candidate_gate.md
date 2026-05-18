# Package 7F: Registry Candidate Gate

Package 7F calibrates the MCP Registry public beta path.

It builds a `public_beta_mcp` candidate dataset from already saved registry metadata, without live network, crawling, scraping, link following, external LLM calls, publishing, or external actions.

## Commands

```powershell
python -m ai_objective_index.registry_intake.registry_beta_dataset_builder
python -m ai_objective_index.registry_intake.registry_quality_audit
python -m ai_objective_index.registry_intake.registry_beta_report_generator
```

## Outputs

- `data/registry/mcp_registry_beta_candidates_v0_1.jsonl`
- `data/registry/mcp_registry_beta_candidate_gate_results_v0_1.json`
- `data/registry/mcp_registry_quality_audit_v0_1.json`
- `data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json`
- `data/registry/mcp_registry_beta_report_v0_1.md`

## Not Implemented

- live network
- broad crawling
- arbitrary website scraping
- link following
- external LLM calls
- supplier verification
- security certification
- payment, booking, login, email, form submission, purchase, account connection, or contract signing

