# MCP Registry Submission Gate

AOI treats MCP Registry submission as a gated action.

The gate checks:

- server JSON exists
- namespace format is valid
- MCP server entrypoint exists
- package artifact or remote MCP endpoint exists where required
- `mcp-publisher` is available
- claim and no-secrets checks are clean

Possible decisions:

- `PASS_SUBMIT_READY`
- `HOLD_PACKAGE_NOT_PUBLISHED`
- `HOLD_NO_REMOTE_MCP_ENDPOINT`
- `HOLD_MCP_PUBLISHER_MISSING`
- `HOLD_AUTH_MISSING`
- `HOLD_SERVER_JSON_DRAFT_ONLY`
- `BLOCK_OVERCLAIM`
- `BLOCK_INVALID_NAMESPACE`

Submission must not run unless the decision is `PASS_SUBMIT_READY` and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set. The helper never unpublishes or deletes registry resources.

Package 8P adds a PyPI package path using `registryType: pypi`. Even with a PyPI-ready server JSON, registry submission remains HOLD until the package is actually uploaded and verified, `mcp-publisher` is available, authentication exists, and explicit confirmation is present.

Package 9A pauses MCP Registry submission until AOI vNext positioning and schemas are aligned. The pause is strategic, not a technical failure.

Package 9B keeps MCP Registry submission paused while CapabilityTrust cards and route decisions are introduced. A future registry submission must not imply verified, safe, security-certified, or quality-guaranteed capabilities.
