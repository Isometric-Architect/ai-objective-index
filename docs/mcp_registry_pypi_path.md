# MCP Registry PyPI Path

MCP Registry can reference a PyPI package with `registryType: pypi`.

Package 8P prepares:

- README marker: `<!-- mcp-name: io.github.isometric-architect/ai-objective-index -->`
- `.mcp/server.json`
- package identifier: `ai-objective-index`
- version: `0.2.0`
- transport: `stdio`

Submission is not automatic. The package must first be uploaded and verified on PyPI. Then run:

```powershell
python -m ai_objective_index.mcp_registry_publish_readiness
```

Only submit later if readiness is `PASS_READY_TO_SUBMIT` and explicit confirmation is present.
