# Package 8R-B: MCP Registry Submit

Package 8R-B installs or locates `mcp-publisher`, authenticates with GitHub, runs preflight, and submits AI Objective Index to the Official MCP Registry only when all gates pass and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set.

Prerequisites:

- real PyPI package exists and installs: `ai-objective-index==0.3.0a1`;
- Package 8S protection gate is PASS;
- `.mcp/server.json` manifest final audit is PASS;
- no real token or claim-boundary findings;
- GitHub auth through `mcp-publisher login github`.

Commands:

```powershell
python -m ai_objective_index.mcp_publisher_installer --check
python -m ai_objective_index.mcp_publisher_installer --instructions
python -m ai_objective_index.mcp_publisher_auth_check --login
python -m ai_objective_index.mcp_registry_publish_preflight
python -m ai_objective_index.mcp_registry_submit_execute --dry-run
$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"
python -m ai_objective_index.mcp_registry_submit_execute --execute
python -m ai_objective_index.mcp_registry_submit_reconcile
python -m ai_objective_index.mcp_registry_discovery_report
```

Registry publication is a metadata listing. It is not verification, security certification, a quality guarantee, product-readiness evidence, purchasing advice, or action authorization.
