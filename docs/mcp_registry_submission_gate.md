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

Package 9C keeps MCP Registry submission paused while Objective Router REST/MCP surfaces are introduced. Registry metadata must not imply the router is a live security gateway or that candidates are verified.

Package 9F adds a vNext distribution gate. MCP Registry submission remains paused until the vNext package version is chosen, the PyPI package exists, `.mcp/server.json` matches that package, and explicit registry confirmation is present.

Package 8Q-A resumed chooses `0.3.0a1` for the local build candidate and refreshes Registry readiness, but does not submit anything.

Package 8Q-C-alt may upload and verify the `0.3.0a1` package on real PyPI because TestPyPI signup is blocked. MCP Registry submission still remains HOLD until `mcp_registry_after_pypi_gate` passes, `mcp-publisher` and registry auth are available, and a later package sets explicit `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.

AOI 0.3.0a2 is the marker-sync recovery path after 0.3.0a1 published successfully but MCP Registry submission still failed with `SERVER_JSON_INVALID`. The recovery gate requires:

- README `mcp-name` marker exactly `io.github.Isometric-Architect/ai-objective-index`;
- `.mcp/server.json` name and package metadata synchronized to `0.3.0a2`;
- real PyPI 0.3.0a2 install verification;
- local `mcp-publisher validate .mcp/server.json` pass;
- no token, overclaim, or private-kernel finding.

Publishing still requires `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` and must not imply security certification, code correctness proof, legal/privacy/license/evaluation proof, product readiness, quality guarantee, or external action authorization.

## Package 8R

Package 8R adds the concrete publisher gate:

- `mcp_publisher_setup` checks for `mcp-publisher`.
- `mcp_registry_manifest_final_audit` validates `.mcp/server.json` against the real PyPI package and README marker.
- `mcp_registry_publish_runner --dry-run` records the planned publish command without submitting.
- `mcp_registry_publish_runner --execute` refuses unless `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set.

Publication, if later completed, is a metadata listing only. It does not certify security, verify quality, establish product readiness, provide purchasing advice, or authorize actions.
