# MCP Registry Submit Runbook

1. Confirm Package 8S gate is PASS:
   `python -m ai_objective_index.mcp_registry_pre_publish_protection_gate`
2. Check publisher:
   `python -m ai_objective_index.mcp_publisher_installer --check`
3. Authenticate:
   `python -m ai_objective_index.mcp_publisher_auth_check --login`
4. Run preflight:
   `python -m ai_objective_index.mcp_registry_publish_preflight`
5. Run dry-run:
   `python -m ai_objective_index.mcp_registry_submit_execute --dry-run`
6. Execute only after explicit confirmation:
   `$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"`
   `python -m ai_objective_index.mcp_registry_submit_execute --execute`
7. Reconcile:
   `python -m ai_objective_index.mcp_registry_submit_reconcile`
8. Write discovery report:
   `python -m ai_objective_index.mcp_registry_discovery_report`

Do not submit if any preflight decision is HOLD or BLOCK.
