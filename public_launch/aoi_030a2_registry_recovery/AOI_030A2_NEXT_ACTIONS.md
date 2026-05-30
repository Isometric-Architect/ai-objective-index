# AOI 0.3.0a2 Next Actions

1. Set `AOI_REAL_PYPI_UPLOAD_CONFIRM=YES` locally only when ready to upload.
2. Run `python -m ai_objective_index.aoi_030a2_pypi_upload_gate`.
3. Enter `__token__` and the PyPI API token only into twine's local prompt.
4. Run `python -m ai_objective_index.aoi_030a2_pypi_verify`.
5. Run `python -m ai_objective_index.aoi_mcp_registry_recovery_gate`.
6. If the gate passes, set `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` locally and run `python -m ai_objective_index.aoi_mcp_registry_recovery_publish`.
7. Run `python -m ai_objective_index.aoi_mcp_registry_recovery_reconcile`.

Do not overwrite or yank 0.3.0a1. Do not commit tokens, `.pypirc`, `mcp-publisher`, temporary virtual environments, or dist artifacts unless a later project policy explicitly allows them.
