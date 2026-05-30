# AOI 0.3.0a2 Failure Recovery

If PyPI reports that `0.3.0a2` already exists, do not overwrite, delete, or yank existing artifacts. Verify the existing package if possible, then choose a later version only after recording the conflict.

If MCP Registry publish reports authentication failure, rerun `mcp-publisher login github` locally and retry the publish runner with `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.

If registry search does not immediately show the entry after a publish success, treat it as propagation HOLD and retry reconcile later.
