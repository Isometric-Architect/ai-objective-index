# Manual Publish Checklist

This is a manual publish checklist. The repository does not publish automatically.

- Review README.
- Run `python -m pytest`.
- Run `python -m ai_objective_index.mcp_smoke`.
- Run `python -m ai_objective_index.datascope_qa`.
- Run `python -m ai_objective_index.beta_readiness`.
- Run `python -m ai_objective_index.release_readiness`.
- Run `python -m ai_objective_index.release_claim_audit`.
- Run `python -m ai_objective_index.registry_intake.mcp_registry_export --use-fixture`.
- Run `python -m ai_objective_index.registry_intake.mcp_registry_eval`.
- Run `python -m ai_objective_index.registry_intake.mcp_registry_report_generator`.
- Run `python -m ai_objective_index.registry_intake.registry_beta_dataset_builder`.
- Run `python -m ai_objective_index.registry_intake.registry_quality_audit`.
- Run `python -m ai_objective_index.registry_intake.registry_beta_report_generator`.
- Create GitHub release manually if desired.
- Create Hugging Face Space manually if desired.
- Create Hugging Face Dataset manually if desired.
- Submit MCP Registry entry manually if desired.
- Post community feedback request manually if desired.
- Do not claim official standard status.
- Do not claim universal adoption.
- Do not claim product quality guarantees, legal/security/compliance certification, or purchasing advice.
