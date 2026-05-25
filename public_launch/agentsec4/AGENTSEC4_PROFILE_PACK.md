# AgentSec-4 Profile Pack

Decision: `PASS_AGENTSEC4_PROFILE_PACK_READY`

AgentSec-4 exposes public-safe policy profile shapes for local MCP/tool metadata review.

| Profile | Mode | Namespace Review | Hold Write | Hold Secret | Hold Code Execution |
| --- | --- | --- | --- | --- | --- |
| `agentsec-local-metadata-only` | `local_metadata_only` | `False` | `True` | `True` | `True` |
| `agentsec-developer-default` | `developer_default` | `True` | `True` | `True` | `True` |
| `agentsec-ci-artifact-review` | `developer_default` | `True` | `True` | `True` | `True` |
| `agentsec-mcp-registry-metadata` | `developer_default` | `True` | `True` | `True` | `True` |
| `agentsec-strict-enterprise` | `strict_enterprise` | `True` | `True` | `True` | `True` |

## Boundary

The profile pack is not a security certification, quality guarantee, product-readiness claim, or action authorization system. It does not call live MCP servers, execute tools, fetch URLs, request tokens, or expose exact private weights, thresholds, provider priors, anti-gaming rules, private negative-control seeds, or commercial routing policy.
