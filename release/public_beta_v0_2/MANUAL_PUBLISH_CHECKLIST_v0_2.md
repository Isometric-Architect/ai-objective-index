# Manual Publish Checklist v0.2

Run locally before any manual public beta release:

- `python -m pytest`
- `python -m ai_objective_index.datascope_qa`
- `python -m ai_objective_index.beta_readiness`
- `python -m ai_objective_index.registry_intake.registry_payload_audit`
- `python -m ai_objective_index.realdata_claim_audit`
- `python -m ai_objective_index.release_candidate_matrix`
- `python -m ai_objective_index.final_preflight`
- `python -m ai_objective_index.public_beta_realdata_packager`
- `python -m ai_objective_index.smoke_all`

Manual steps only:

- Publish a GitHub release manually if desired.
- Publish a Hugging Face Space or Dataset manually if desired.
- Post community feedback request manually if desired.
- Do not claim verified MCP servers, safe MCP servers, security certification, quality guarantee, purchasing advice, official standard status, or universal adoption.
