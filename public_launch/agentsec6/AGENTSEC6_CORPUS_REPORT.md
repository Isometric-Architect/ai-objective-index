# AgentSec-6 Local Manifest Corpus Report

Decision: `PASS_AGENTSEC6_LOCAL_CORPUS_INTAKE`

| Field | Value |
| --- | --- |
| Manifests | `5` |
| Policy gate | `BLOCK_AGENTSEC2_POLICY_RISK` |
| ALLOW metadata-only | `1` |
| HOLD review | `2` |
| BLOCK policy risk | `2` |
| Live MCP calls | `False` |
| External tool execution | `False` |
| URL fetch | `False` |

## Packet Decisions

| Tool | Decision | Integration | Provider |
| --- | --- | --- | --- |
| `fixture.local/local-metadata-reader` | `ALLOW_METADATA_ONLY` | `mcp_server` | `local-fixture` |
| `fixture.local/browser-research-helper` | `HOLD_REVIEW_REQUIRED` | `mcp_server` | `local-fixture` |
| `fixture.local/repo-file-review-helper` | `HOLD_REVIEW_REQUIRED` | `tool_manifest` | `local-fixture` |
| `fixture.local/checkout-helper` | `BLOCK_FORBIDDEN_ACTION` | `agent_tool` | `local-fixture` |
| `fixture.local/security-claim-helper` | `BLOCK_UNSUPPORTED_CLAIM` | `api` | `local-fixture` |

## Warnings

- No warnings recorded.

## Errors

- No errors recorded.

## Boundary

AgentSec-6 is a local manifest corpus ingestion artifact. It does not call live MCP servers, execute tools, fetch URLs, handle tokens, certify security, guarantee quality, prove product readiness, provide live gateway protection, or authorize external actions.
