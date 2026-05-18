# MCP Stdio Local Test

Run the local smoke test:

```powershell
python -m ai_objective_index.mcp_smoke
```

Expected output includes:

```text
MCP smoke: pass=True
```

Run the stdio entrypoint:

```powershell
python -m ai_objective_index.mcp_stdio_entrypoint
```

If the MCP SDK is missing, expected fallback:

```text
MCP SDK not installed. Use mcp_tools functions, manifest, or install optional dependency.
```

If the SDK is installed, the entrypoint starts a local stdio MCP server. It exposes only read-only tools.
