# AgentSec-5 Fixture Corpus

Decision: `PASS_AGENTSEC5_FIXTURE_CORPUS_READY`

AgentSec-5 adds public-safe fake MCP/tool manifest fixtures for local negative-control testing.

| Fixture | Risk Theme | Expected Decision |
| --- | --- | --- |
| `safe-local-metadata` | `safe_metadata_shape` | `ALLOW_METADATA_ONLY` |
| `network-browser-access` | `permission_scope_review` | `HOLD_REVIEW_REQUIRED` |
| `hidden-instruction` | `hidden_instruction_review` | `HOLD_REVIEW_REQUIRED` |
| `official-like-namespace` | `namespace_ownership_review` | `HOLD_REVIEW_REQUIRED` |
| `unsupported-safety-claim` | `unsupported_positive_claim` | `BLOCK_UNSUPPORTED_CLAIM` |
| `forbidden-real-world-action` | `forbidden_action_language` | `BLOCK_FORBIDDEN_ACTION` |
| `secret-exfiltration-language` | `secret_and_exfiltration_review` | `HOLD_REVIEW_REQUIRED` |

## Boundary

The corpus contains fake local fixtures only. It does not include real provider secrets, private ranking weights, private thresholds, provider priors, private negative-control seeds, a live security scanner, security certification, quality guarantee, product-readiness proof, or action authorization.
