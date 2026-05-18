# Package 7D MCP Registry Intake

Package 7D adds an Official MCP Registry intake pilot for AOI. It converts registry-style metadata into AOI `ActionObject` and `SourceTrace` records, validates those records, and exposes `mcp_registry` and `public_beta_mcp` data scopes.

## Commands

Offline fixture export:

```powershell
python -m ai_objective_index.registry_intake.mcp_registry_export --use-fixture
```

Eval:

```powershell
python -m ai_objective_index.registry_intake.mcp_registry_eval
```

Report:

```powershell
python -m ai_objective_index.registry_intake.mcp_registry_report_generator
```

Optional live registry API mode:

```powershell
python -m ai_objective_index.registry_intake.mcp_registry_export --allow-network --use-fixture false --max-servers 50
```

Do not run live mode unless the project owner explicitly requests it.

## Intentionally Not Implemented

Package 7D does not implement broad crawling, arbitrary scraping, link following, external LLM calls, publishing, registry submission, supplier verification, payment, booking, login, email sending, form submission, purchase, account connection, or contract signing.

