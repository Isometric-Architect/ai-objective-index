# AgentSec MCP Manifest Hardening

AgentSec-4 also adds a static hardening check for AOI MCP surfaces:

- `data/generated_mcp_tools_manifest.json`
- `.mcp/server.json`

The hardening check verifies read-only flags, tool schemas, forbidden action boundaries, conservative limitations, and absence of unsupported positive claims.

Run:

```powershell
python -m ai_objective_index.agentsec.mcp_manifest_hardening --write-sample
python -m ai_objective_index.agentsec.package4
```

This is a static manifest review. It is not a live security scanner, security certification, quality guarantee, product-readiness proof, or action authorization.
