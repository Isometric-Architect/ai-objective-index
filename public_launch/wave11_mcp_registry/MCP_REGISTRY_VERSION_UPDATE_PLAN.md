# MCP Registry Version Update Plan

If `0.3.0a1` already exists in the registry or the publish partially succeeds, do not retry blindly with the same files.

Recommended recovery path:

1. Fix the package or manifest issue locally.
2. Bump package and server version to the next prerelease, such as `0.3.0a2`.
3. Build and verify the new PyPI package.
4. Upload the new PyPI version.
5. Update `.mcp/server.json`.
6. Run the MCP Registry manifest final audit again.
7. Publish only after explicit confirmation.

Do not delete or unpublish as the normal update workflow.
