# AOI 0.3.0a2 Final Publish

AOI 0.3.0a2 is the final marker-sync and agent-surface package candidate for real PyPI upload and MCP Registry publication.

Run the local preflight first:

```powershell
python -m ai_objective_index.aoi_030a2_final_preflight
python -m ai_objective_index.aoi_030a2_build_verify
python -m ai_objective_index.agent_adoption.package_data_audit
python -m ai_objective_index.agent_adoption.agent_surface_audit
python -m ai_objective_index.aoi_030a2_final_pypi_upload_gate
```

The final package keeps the canonical MCP name `io.github.Isometric-Architect/ai-objective-index`, PyPI identifier `ai-objective-index`, and version `0.3.0a2`.

Real PyPI upload requires `AOI_REAL_PYPI_UPLOAD_CONFIRM=YES` and interactive `twine` credential entry. MCP Registry publish requires real PyPI install verification, local `mcp-publisher validate`, and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.

This final publish flow does not store tokens, create `.pypirc`, commit dist artifacts by default, commit `mcp-publisher`, overwrite or yank `0.3.0a1`, claim security certification, prove correctness, claim legal/privacy/license clearance, guarantee quality, claim product readiness, or authorize actions.

