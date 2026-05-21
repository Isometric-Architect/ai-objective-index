# MCP Registry Failure Recovery

- Missing publisher: install `mcp-publisher` manually and rerun the check.
- Login failure: rerun GitHub login and complete browser/device auth.
- Manifest mismatch: align `.mcp/server.json`, README marker, PyPI version, and repository URL.
- Protection gate HOLD/BLOCK: fix exposure or license/package-artifact findings before retry.
- Version already exists: bump to `0.3.0a2`, publish PyPI first, then update server JSON.
- Publish succeeds but search not visible: wait for registry propagation and rerun reconcile.

Do not delete/unpublish as the normal workflow. Do not claim the registry listing is security certification or quality validation.
