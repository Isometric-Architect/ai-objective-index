# DataCapsule-2 Corpus Manifest Report

Decision: `BLOCK_DATACAPSULE2_USE_RISK`

| Field | Value |
| --- | --- |
| Corpus ID | `fixture.local/aoi-docs-corpus-manifest` |
| Name | `AOI local docs corpus manifest fixture` |
| File count | `3` |
| Source record count | `3` |
| Negative-control false passes | `0` |
| Network used | `False` |
| Crawler used | `False` |
| External service used | `False` |

## Use Boundaries

| Use | Decision | Allowed |
| --- | --- | --- |
| `train` | `HOLD_SOURCE_RIGHTS_REVIEW` | `False` |
| `retrieve` | `HOLD_STALENESS_REVIEW` | `False` |
| `evaluate` | `HOLD_SOURCE_RIGHTS_REVIEW` | `False` |
| `summarize` | `HOLD_STALENESS_REVIEW` | `False` |
| `share` | `HOLD_SOURCE_RIGHTS_REVIEW` | `False` |
| `act` | `BLOCK_ACTION_USE` | `False` |

## Negative Controls

| Control | Expected | Actual | Result |
| --- | --- | --- | --- |
| `unsupported_claim_blocks` | `BLOCK_UNSUPPORTED_CLAIM` | `BLOCK_UNSUPPORTED_CLAIM` | `PASS_NEGATIVE_CONTROL` |
| `no_source_holds` | `HOLD_SOURCE_RIGHTS_REVIEW` | `HOLD_SOURCE_RIGHTS_REVIEW` | `PASS_NEGATIVE_CONTROL` |
| `prompt_injection_holds` | `HOLD_PROMPT_INJECTION_REVIEW` | `HOLD_PROMPT_INJECTION_REVIEW` | `PASS_NEGATIVE_CONTROL` |
| `action_use_blocks` | `BLOCK_ACTION_USE` | `BLOCK_ACTION_USE` | `PASS_NEGATIVE_CONTROL` |

## Missing Fields

- No missing manifest fields recorded.

## Boundaries

DataCapsule-2 is a local corpus-manifest receipt. It does not inspect private file contents, crawl directories, fetch URLs, prove legal sufficiency, prove privacy compliance, guarantee data quality, prove evaluation cleanliness, or authorize actions.
