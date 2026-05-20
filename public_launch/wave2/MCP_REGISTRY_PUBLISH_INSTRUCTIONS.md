# MCP Registry Publish Instructions

1. Confirm PyPI package `ai-objective-index` version `0.2.0` is public.
2. Confirm README contains:

```html
<!-- mcp-name: io.github.isometric-architect/ai-objective-index -->
```

3. Confirm `.mcp/server.json` uses `registryType: pypi`.
4. Run:

```powershell
python -m ai_objective_index.mcp_registry_publish_readiness
```

5. Submit only if readiness is `PASS_READY_TO_SUBMIT`.
6. Set explicit confirmation only when ready:

```powershell
$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"
```

7. Then use the dedicated MCP publisher flow.

Package 8P does not submit to MCP Registry.
