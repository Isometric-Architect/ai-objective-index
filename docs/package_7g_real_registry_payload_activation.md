# Package 7G: Real Registry Payload Activation

Package 7G preserves and activates real/manual MCP Registry raw payloads, then rebuilds registry outputs without live network.

## Commands

```powershell
python -m ai_objective_index.registry_intake.real_payload_activation --use-existing-raw
python -m ai_objective_index.registry_intake.registry_payload_audit
python -m ai_objective_index.registry_intake.registry_reprocess_all
```

Optional explicit live mode, only if the project owner asks for it:

```powershell
python -m ai_objective_index.registry_intake.real_payload_activation --try-live --max-servers 50
```

## Outputs

- `data/registry/real_payload_activation_result_v0_1.json`
- `data/registry/registry_payload_audit_v0_1.json`
- `data/registry/registry_reprocess_all_result_v0_1.json`

## Not Implemented

- broad crawling
- arbitrary scraping
- link following
- repository/docs/package page fetching
- external LLM calls
- publishing
- registry submission
- payment, booking, login, email, form submission, purchase, account connection, supplier verification, or contract signing

