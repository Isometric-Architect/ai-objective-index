# AOI MCP Registry Publish Recovery

MCP Registry recovery is intentionally gated.

Before publish:

- PyPI 0.3.0a2 must be uploaded and install-verified.
- README marker and `.mcp/server.json` metadata must match.
- `mcp-publisher validate .mcp/server.json` must pass locally.
- no-secrets, claim guard, and technology protection checks must pass.
- `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` must be set locally.

Publish helper:

```powershell
python -m ai_objective_index.aoi_mcp_registry_recovery_gate
python -m ai_objective_index.aoi_mcp_registry_recovery_publish
python -m ai_objective_index.aoi_mcp_registry_recovery_reconcile
```

The publish helper does not run when the gate is not PASS or the confirmation variable is absent. The registry listing is a metadata listing only. It does not certify security, prove correctness, clear legal/privacy/license/evaluation status, guarantee quality, show product readiness, or authorize actions.
