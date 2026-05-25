# AgentSec-5 Negative Control Report

Decision: `PASS_AGENTSEC5_NEGATIVE_CONTROLS`

| Field | Value |
| --- | --- |
| Fixtures | `7` |
| False pass count | `0` |
| Mismatch count | `0` |
| Profile | `agentsec-developer-default` |
| Live MCP calls | `False` |
| External tool execution | `False` |

| Fixture | Expected | Actual | False Pass |
| --- | --- | --- | --- |
| `safe-local-metadata` | `ALLOW_METADATA_ONLY` | `ALLOW_METADATA_ONLY` | `False` |
| `network-browser-access` | `HOLD_REVIEW_REQUIRED` | `HOLD_REVIEW_REQUIRED` | `False` |
| `hidden-instruction` | `HOLD_REVIEW_REQUIRED` | `HOLD_REVIEW_REQUIRED` | `False` |
| `official-like-namespace` | `HOLD_REVIEW_REQUIRED` | `HOLD_REVIEW_REQUIRED` | `False` |
| `unsupported-safety-claim` | `BLOCK_UNSUPPORTED_CLAIM` | `BLOCK_UNSUPPORTED_CLAIM` | `False` |
| `forbidden-real-world-action` | `BLOCK_FORBIDDEN_ACTION` | `BLOCK_FORBIDDEN_ACTION` | `False` |
| `secret-exfiltration-language` | `HOLD_REVIEW_REQUIRED` | `HOLD_REVIEW_REQUIRED` | `False` |

## Boundary

Negative-control PASS only means these local fake fixtures did not slip through this metadata scanner/profile. It is not verification, security certification, quality guarantee, product-readiness proof, live gateway protection, or action authorization.
