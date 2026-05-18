# Package 7E Live MCP Registry Intake

Package 7E adds a controlled live-run wrapper for the Official MCP Registry API.

Default mode uses no network:

```powershell
python -m ai_objective_index.registry_intake.live_registry_run
```

If `data/registry/mcp_registry_raw_v0_1.json` exists, default mode processes it as local manual raw data. If no raw file exists, it writes fallback status and exits gracefully.

Explicit live mode:

```powershell
python -m ai_objective_index.registry_intake.live_registry_run --allow-network --max-servers 50
```

Live mode only uses read-only `GET /v0.1/servers?limit=50` against `https://registry.modelcontextprotocol.io`.

## Boundaries

- no broad crawling;
- no arbitrary web scraping;
- no link following;
- no GitHub/package/doc page fetches;
- no tokens or credentials;
- no external LLM APIs;
- no publishing or registry submission;
- no payment, booking, login, email, form submission, purchase, account connection, supplier verification, or contract signing.

All mapped objects remain `EXTRACTED_UNVERIFIED`. Registry metadata is not a security certification or supplier verification.

