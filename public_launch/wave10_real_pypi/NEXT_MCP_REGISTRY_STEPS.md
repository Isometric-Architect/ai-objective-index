# Next MCP Registry Steps

MCP Registry submission remains out of scope for Package 8Q-C-alt.

After real PyPI upload and install verification pass:

1. Run `python -m ai_objective_index.mcp_registry_after_pypi_gate`.
2. Install or locate `mcp-publisher` if the gate reports `HOLD_MCP_PUBLISHER_REQUIRED`.
3. Confirm registry authentication locally.
4. Run a registry dry-run or readiness check first.
5. Submit only in a later package with explicit confirmation.

Required future publish confirmation:

```powershell
$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"
```

Do not submit MCP Registry metadata from Package 8Q-C-alt.
