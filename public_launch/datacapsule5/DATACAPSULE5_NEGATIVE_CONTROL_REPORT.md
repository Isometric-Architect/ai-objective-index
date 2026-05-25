# DataCapsule-5 Negative Control Report

Decision: `PASS_DATACAPSULE5_NEGATIVE_CONTROLS`

| Field | Value |
| --- | --- |
| Fixtures | `9` |
| False pass count | `0` |
| Mismatch count | `0` |
| Network used | `False` |
| Crawler used | `False` |

| Fixture | Primary Use | Expected | Actual | False Pass |
| --- | --- | --- | --- | --- |
| `safe-retrieval-public-docs` | `retrieve` | `ALLOW_USE` | `ALLOW_USE` | `False` |
| `unknown-license-training` | `train` | `HOLD_SOURCE_RIGHTS_REVIEW` | `HOLD_SOURCE_RIGHTS_REVIEW` | `False` |
| `restricted-license-training` | `train` | `BLOCK_LICENSE_RESTRICTED` | `BLOCK_LICENSE_RESTRICTED` | `False` |
| `privacy-risk-training` | `train` | `BLOCK_PRIVACY_RISK` | `BLOCK_PRIVACY_RISK` | `False` |
| `prompt-injection-retrieval` | `retrieve` | `HOLD_PROMPT_INJECTION_REVIEW` | `HOLD_PROMPT_INJECTION_REVIEW` | `False` |
| `eval-leak-evaluation` | `evaluate` | `HOLD_EVAL_LEAK_REVIEW` | `HOLD_EVAL_LEAK_REVIEW` | `False` |
| `unsupported-claim-metadata` | `retrieve` | `BLOCK_UNSUPPORTED_CLAIM` | `BLOCK_UNSUPPORTED_CLAIM` | `False` |
| `missing-source-record` | `retrieve` | `HOLD_SOURCE_RIGHTS_REVIEW` | `HOLD_SOURCE_RIGHTS_REVIEW` | `False` |
| `action-use-request` | `act` | `BLOCK_ACTION_USE` | `BLOCK_ACTION_USE` | `False` |

## Boundary

Negative-control PASS only means these local fake data-use fixtures did not slip through this metadata capsule builder. It is not legal review, privacy certification, data-quality certification, evaluation-cleanliness proof, live source verification, or action authorization.
