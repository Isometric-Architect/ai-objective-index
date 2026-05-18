# MCP Registry Manual Download Fallback

Use this only for the Official MCP Registry JSON endpoint. Do not provide tokens or credentials. Do not scrape arbitrary pages. Do not log in.

## Option A: Browser

1. Open:

```text
https://registry.modelcontextprotocol.io/v0.1/servers?limit=50
```

2. Save the page as JSON or copy all text.
3. Put it at:

```text
data/registry/mcp_registry_raw_v0_1.json
```

If you already put the file at the repository root as `mcp_registry_raw_v0_1.json`, AOI can activate it with the same command below.

4. Run:

```powershell
python -m ai_objective_index.registry_intake.real_payload_activation --use-existing-raw
python -m ai_objective_index.registry_intake.registry_reprocess_all
```

## Option B: Windows PowerShell

```powershell
curl.exe "https://registry.modelcontextprotocol.io/v0.1/servers?limit=50" -o data\registry\mcp_registry_raw_v0_1.json
```

## Option C: macOS/Linux

```bash
curl "https://registry.modelcontextprotocol.io/v0.1/servers?limit=50" -o data/registry/mcp_registry_raw_v0_1.json
```

After saving:

```powershell
python -m ai_objective_index.registry_intake.real_payload_activation --use-existing-raw
python -m ai_objective_index.registry_intake.registry_payload_audit
python -m ai_objective_index.registry_intake.registry_reprocess_all
```

All records remain `EXTRACTED_UNVERIFIED`. Registry metadata is not supplier verification, security certification, quality guarantee, purchasing advice, or action permission.
