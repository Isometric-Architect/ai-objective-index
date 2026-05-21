# MCP Registry Publish Safety

MCP Registry publication should be treated as metadata distribution, not as certification.

Safe path:

1. Confirm real PyPI install verification passed.
2. Confirm `.mcp/server.json` matches `io.github.isometric-architect/ai-objective-index`.
3. Confirm README contains the matching `mcp-name` marker.
4. Run the manifest final audit.
5. Install and authenticate `mcp-publisher`.
6. Run dry-run first.
7. Submit only with `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.

Do not paste GitHub tokens into chat. Do not commit token files or `.pypirc`. If a credential is exposed, revoke it.

AOI remains read-only. Registry publication does not authorize payment, booking, login, email, purchase, contract signing, account connection, supplier verification, or profile modification.
