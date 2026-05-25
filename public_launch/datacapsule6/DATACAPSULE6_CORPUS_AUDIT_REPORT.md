# DataCapsule-6 Repository Corpus Audit Report

Generated: `2026-05-25T02:37:29.068848+00:00`

DataCapsule-6 packages local DataCapsule-5 fixture corpus and negative-control outputs into reviewer-facing artifacts. It is for human review of repository-supplied data-use metadata patterns.

## Decision

| Field | Value |
| --- | --- |
| DataCapsule-6 bundle | `PASS_DATACAPSULE6_REPOSITORY_AUDIT_BUNDLE` |
| DataCapsule-5 package | `PASS_DATACAPSULE5_FIXTURE_CORPUS_AND_NEGATIVE_CONTROLS` |
| Fixture corpus | `PASS_DATACAPSULE5_FIXTURE_CORPUS_READY` |
| Negative controls | `PASS_DATACAPSULE5_NEGATIVE_CONTROLS` |
| Fixtures | `9` |
| Actual ALLOW | `1` |
| Actual HOLD | `4` |
| Actual BLOCK | `4` |
| False passes | `0` |
| Mismatches | `0` |
| Crawler used | `False` |
| Network used | `False` |
| External service used | `False` |
| Review comment posted | `False` |

## Fixture Corpus

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

## Negative-Control Outcomes

| Fixture | Expected | Actual | False Pass |
| --- | --- | --- | --- |
| `safe-retrieval-public-docs` | `ALLOW_USE` | `ALLOW_USE` | `False` |
| `unknown-license-training` | `HOLD_SOURCE_RIGHTS_REVIEW` | `HOLD_SOURCE_RIGHTS_REVIEW` | `False` |
| `restricted-license-training` | `BLOCK_LICENSE_RESTRICTED` | `BLOCK_LICENSE_RESTRICTED` | `False` |
| `privacy-risk-training` | `BLOCK_PRIVACY_RISK` | `BLOCK_PRIVACY_RISK` | `False` |
| `prompt-injection-retrieval` | `HOLD_PROMPT_INJECTION_REVIEW` | `HOLD_PROMPT_INJECTION_REVIEW` | `False` |
| `eval-leak-evaluation` | `HOLD_EVAL_LEAK_REVIEW` | `HOLD_EVAL_LEAK_REVIEW` | `False` |
| `unsupported-claim-metadata` | `BLOCK_UNSUPPORTED_CLAIM` | `BLOCK_UNSUPPORTED_CLAIM` | `False` |
| `missing-source-record` | `HOLD_SOURCE_RIGHTS_REVIEW` | `HOLD_SOURCE_RIGHTS_REVIEW` | `False` |
| `action-use-request` | `BLOCK_ACTION_USE` | `BLOCK_ACTION_USE` | `False` |

## Reviewer Notes

- `ALLOW_USE` means the local public metadata fixture did not trigger a hold or block for that requested use.
- `HOLD_*` means the metadata needs source, rights, privacy, prompt-injection, or eval-leak review before use.
- `BLOCK_*` means the metadata is unsuitable for the requested use under the public local rules.
- This report is generated from local artifacts and does not crawl directories, inspect private file contents, fetch URLs, call external services, post comments, or handle tokens.

## Must Not Claim

- Do not claim legal sufficiency.
- Do not claim privacy compliance.
- Do not claim data quality guarantee.
- Do not claim license clearance.
- Do not claim evaluation cleanliness.
- Do not claim purchasing advice.
- Do not claim action authorization.
