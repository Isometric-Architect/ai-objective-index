# Smoke Test Commands v0.2

```powershell
python -m pytest
python -m ai_objective_index.realdata_claim_audit
python -m ai_objective_index.release_candidate_matrix
python -m ai_objective_index.final_preflight
python -m ai_objective_index.public_beta_realdata_packager
python -m ai_objective_index.smoke_all
```

Expected: commands complete locally, no network is required, no publish occurs, and no forbidden actions are exposed.
