# AgentSec-2 Policy Gate Report

Decision: `BLOCK_AGENTSEC2_POLICY_RISK`

| Field | Value |
| --- | --- |
| Profile | `agentsec-developer-default` |
| Packets | `3` |
| ALLOW metadata-only | `1` |
| HOLD review | `1` |
| BLOCK policy risk | `1` |
| Live MCP calls | `False` |
| External tool execution | `False` |
| URL fetch | `False` |

## Packet Decisions

| Tool | Decision | Integration | Provider |
| --- | --- | --- | --- |
| `fixture.local/local-metadata-browser-helper` | `ALLOW_METADATA_ONLY` | `mcp_server` | `local-fixture` |
| `fixture.local/repo-file-review-helper` | `HOLD_REVIEW_REQUIRED` | `mcp_server` | `local-fixture` |
| `fixture.local/checkout-action-helper` | `BLOCK_FORBIDDEN_ACTION` | `agent_tool` | `local-fixture` |

## Hold Reasons

- fixture.local/checkout-action-helper: policy holds network_access
- fixture.local/repo-file-review-helper: policy holds file_access

## Block Reasons

- fixture.local/checkout-action-helper: forbidden action language

## Boundaries

AgentSec-2 is a local metadata policy gate. It does not certify security, guarantee quality, claim product readiness, execute tools, call live MCP servers, fetch URLs, handle tokens, or authorize external actions.
