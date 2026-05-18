# Smoke Test Matrix

Run these local commands before manual public beta publishing:

| Command | Expected output |
| --- | --- |
| `python -m pytest` | tests pass |
| `python -m ai_objective_index.mcp_smoke` | `pass=True` |
| `python -m ai_objective_index.datascope_qa` | QA JSON generated, no live network |
| `python -m ai_objective_index.beta_readiness` | beta readiness report generated |
| `python -m ai_objective_index.release_readiness` | release readiness JSON generated |
| `python -m ai_objective_index.release_claim_audit` | claim audit JSON generated |
| `python -m ai_objective_index.public_beta_packager` | release pack generated |
| `python -m ai_objective_index.smoke_all` | smoke result JSON generated |

All smoke tests are local-only and read-only.
