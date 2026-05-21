# Package 8R: MCP Registry Publish Gate

Package 8R prepares AI Objective Index for Official MCP Registry publication after the real PyPI upload of `ai-objective-index==0.3.0a1`.

It adds setup checks for `mcp-publisher`, a final `.mcp/server.json` audit, a dry-run publish runner, post-publish verification, and a release audit. Registry publication is a metadata listing only. It is not verification, security certification, a quality guarantee, product-readiness evidence, purchasing advice, or action authorization.

## Commands

```powershell
python -m ai_objective_index.mcp_publisher_setup --check
python -m ai_objective_index.mcp_registry_manifest_final_audit
python -m ai_objective_index.mcp_registry_publish_runner --dry-run
python -m ai_objective_index.mcp_registry_publish_runner --login
$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"
python -m ai_objective_index.mcp_registry_publish_runner --execute
python -m ai_objective_index.mcp_registry_post_publish_verify
python -m ai_objective_index.mcp_registry_release_audit
```

Do not run `--execute` unless the manifest audit passes, `mcp-publisher` is available, GitHub auth succeeds, and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set.

## Boundaries

- Do not paste GitHub or registry tokens into chat.
- Do not commit credentials.
- Do not upload a new PyPI version in this package.
- Do not post to communities.
- Do not claim AOI is verified, safe, security certified, quality guaranteed, or product ready.
