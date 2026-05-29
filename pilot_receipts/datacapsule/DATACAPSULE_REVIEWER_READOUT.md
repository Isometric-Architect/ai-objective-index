# DataCapsule Pilot Reviewer Readout

## What Was Reviewed

- Pilot: `datacapsule-pilot-f13cbbb5bb96`
- Corpus: `DataCapsule local sample corpus`
- Source type: `sample_fixture`
- Capsule decision: `BLOCK_ACTION_USE`

## Scope

- Local/offline manifest metadata review only.
- Raw corpus content was not inspected.
- No crawling, URL fetching, upload, model training, external API call, or GitHub API call.

## ALLOW/HOLD/BLOCK Summary

| Decision | Count |
| --- | ---: |
| ALLOW | `1` |
| HOLD | `1` |
| BLOCK | `1` |

## Source / Rights Summary

- Rights status: `HOLD_LICENSE_MISSING`
- Missing fields: `declared_license, declared_terms, declared_collection_method`

## Privacy Risk Summary

- Privacy status: `HOLD_PII_UNKNOWN`
- Missing fields: `declared_pii_status, declared_retention_policy`

## Evaluation Boundary Summary

- Leakage status: `HOLD_EVAL_OVERLAP_UNKNOWN`
- Missing fields: `declared_eval_overlap_status, split_policy`

## Use Boundary

| Use | Decision |
| --- | --- |
| train | `HOLD` |
| retrieve | `ALLOW` |
| evaluate | `HOLD` |
| share | `HOLD` |
| act | `BLOCK` |
| commercial | `HOLD` |

## Findings

| Finding | Decision | Severity | Category | Explanation | Next Action |
| --- | --- | --- | --- | --- | --- |
| datacapsule-pilot-finding-1 | ALLOW | info | retrieve_boundary | Manifest review artifact can record declared retrieval use as a local metadata signal. | keep as manifest-only review evidence |
| datacapsule-pilot-finding-2 | HOLD | medium | license_gap | Manifest metadata has rights, privacy, evaluation-boundary, or staleness gaps. | request license, terms, privacy, consent, split-policy, and update-date evidence |
| datacapsule-pilot-finding-3 | BLOCK | high | act_boundary | Action use is blocked and declared disallowed uses cannot be upgraded by a manifest-only pilot. | keep action use blocked unless separately authorized by a future owner-approved process |

## Known Limits

- Not a legal opinion.
- Not a privacy audit.
- Not license clearance.
- Not evaluation-cleanliness proof.
- Not a data quality guarantee.
- No training authorization.
- No action authorization.
