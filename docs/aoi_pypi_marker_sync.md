# AOI PyPI Marker Sync

The PyPI package README and `.mcp/server.json` must agree on the MCP server name before MCP Registry submission.

Required marker:

```text
mcp-name: io.github.Isometric-Architect/ai-objective-index
```

Required 0.3.0a2 files:

- `pyproject.toml`: `0.3.0a2`
- `src/ai_objective_index/__init__.py`: `0.3.0a2`
- `.mcp/server.json` top-level version: `0.3.0a2`
- `.mcp/server.json` PyPI package version: `0.3.0a2`
- README marker: exact-case canonical server name

Run:

```powershell
python -m ai_objective_index.aoi_030a2_marker_sync
python -m ai_objective_index.aoi_030a2_build_verify
```

Do not commit `.pypirc`, tokens, temporary virtual environments, `mcp-publisher`, or dist files unless a later policy explicitly allows those artifacts.
