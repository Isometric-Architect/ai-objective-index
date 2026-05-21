# MCP Registry Failure Recovery Plan

- If `mcp-publisher` is missing: install it manually from the official `modelcontextprotocol/registry` release source and rerun the installer check.
- If GitHub auth fails: rerun `python -m ai_objective_index.mcp_publisher_auth_check --login`.
- If namespace or README marker mismatches: fix `.mcp/server.json` and the README `mcp-name` marker, then rerun preflight.
- If version already exists: bump to `0.3.0a2`, publish PyPI first, then retry registry publication.
- If publish succeeds but search is not visible: wait for propagation and rerun reconcile.
- Do not delete or unpublish as the normal workflow.
- Do not paste tokens into chat, and do not commit credentials.
