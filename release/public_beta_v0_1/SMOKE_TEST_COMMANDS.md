# Smoke Test Commands

```powershell
python -m pytest
python -m ai_objective_index.mcp_smoke
python -m ai_objective_index.datascope_qa
python -m ai_objective_index.beta_readiness
python -m ai_objective_index.release_readiness
python -m ai_objective_index.release_claim_audit
python -m ai_objective_index.public_beta_packager
python -m ai_objective_index.smoke_all
python -m ai_objective_index.registry_intake.mcp_registry_export --use-fixture
python -m ai_objective_index.registry_intake.mcp_registry_eval
python -m ai_objective_index.registry_intake.mcp_registry_report_generator
python -m ai_objective_index.registry_intake.registry_beta_dataset_builder
python -m ai_objective_index.registry_intake.registry_quality_audit
python -m ai_objective_index.registry_intake.registry_beta_report_generator
```

Expected: commands complete locally without network access, no live crawling, and no actual publishing.
