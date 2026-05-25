# DataCapsule-5 Fixture Corpus

Decision: `PASS_DATACAPSULE5_FIXTURE_CORPUS_READY`

DataCapsule-5 adds public-safe fake data-use metadata fixtures for local negative-control testing.

| Fixture | Primary Use | Risk Theme | Expected Decision |
| --- | --- | --- | --- |
| `safe-retrieval-public-docs` | `retrieve` | `source_traced_retrieval_metadata` | `ALLOW_USE` |
| `unknown-license-training` | `train` | `rights_unknown` | `HOLD_SOURCE_RIGHTS_REVIEW` |
| `restricted-license-training` | `train` | `restricted_license` | `BLOCK_LICENSE_RESTRICTED` |
| `privacy-risk-training` | `train` | `privacy_risk` | `BLOCK_PRIVACY_RISK` |
| `prompt-injection-retrieval` | `retrieve` | `prompt_injection_review` | `HOLD_PROMPT_INJECTION_REVIEW` |
| `eval-leak-evaluation` | `evaluate` | `eval_leak_review` | `HOLD_EVAL_LEAK_REVIEW` |
| `unsupported-claim-metadata` | `retrieve` | `unsupported_positive_claim` | `BLOCK_UNSUPPORTED_CLAIM` |
| `missing-source-record` | `retrieve` | `source_trace_missing` | `HOLD_SOURCE_RIGHTS_REVIEW` |
| `action-use-request` | `act` | `action_authorization_boundary` | `BLOCK_ACTION_USE` |

## Boundary

The corpus contains fake local fixtures only. It does not include real private datasets, hidden rights analysis, private ranking weights, private thresholds, private negative-control seeds, legal review, privacy certification, data-quality certification, evaluation-cleanliness proof, or action authorization.
