# AOI MCP Registry Final Publish

MCP Registry publication happens only after real PyPI install verification passes for `ai-objective-index==0.3.0a2`.

Final gate:

```powershell
python -m ai_objective_index.aoi_030a2_final_mcp_registry_gate
```

If the gate reports that only the environment confirmation is missing:

```powershell
.\tools\mcp-publisher\mcp-publisher.exe login github
$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"
python -m ai_objective_index.aoi_030a2_final_mcp_registry_publish --execute
python -m ai_objective_index.aoi_030a2_final_mcp_registry_reconcile
```

Publisher output is redacted before it is written to local result files. Do not paste GitHub tokens into chat, commit `mcp-publisher.exe`, force-push, post to communities, or treat Registry publication as verification, security certification, product readiness, legal/privacy/license clearance, quality guarantee, proof, or action authorization.

