# MCP Registry After PyPI

MCP Registry submission remains gated after real PyPI upload.

The post-PyPI gate checks:

- real PyPI upload result;
- real PyPI install verification;
- `.mcp/server.json` uses `registryType: pypi`;
- package identifier is `ai-objective-index`;
- version is `0.3.0a1`;
- README `mcp-name` marker matches the server name;
- no token findings;
- no overclaiming.

Run:

```powershell
python -m ai_objective_index.mcp_registry_after_pypi_gate
```

Expected next state after real PyPI install passes is either `PASS_READY_FOR_MCP_REGISTRY_DRY_RUN` or `HOLD_MCP_PUBLISHER_REQUIRED`.

Do not submit MCP Registry metadata until a later package explicitly confirms publisher availability, registry authentication, and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.
