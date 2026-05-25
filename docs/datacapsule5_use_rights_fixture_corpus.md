# DataCapsule-5 Use-Rights Fixture Corpus

DataCapsule-5 adds a public-safe fake fixture corpus for local use-boundary regression checks. It focuses on source and rights review, restricted license metadata, privacy risk, prompt-injection metadata, eval-leak separation, unsupported positive claims, missing source records, and action-use boundaries.

Run:

```bash
python -m ai_objective_index.datacapsule.fixture_corpus --write-sample
python -m ai_objective_index.datacapsule.negative_controls --write-sample
python -m ai_objective_index.datacapsule.package5
python -m ai_objective_index.datacapsule_claim_audit
```

Generated outputs:

- `public_launch/datacapsule5/DATACAPSULE5_FIXTURE_CORPUS.json`
- `public_launch/datacapsule5/DATACAPSULE5_FIXTURE_CORPUS_REPORT.md`
- `public_launch/datacapsule5/DATACAPSULE5_NEGATIVE_CONTROL_RESULT.json`
- `public_launch/datacapsule5/DATACAPSULE5_NEGATIVE_CONTROL_REPORT.md`
- `public_launch/datacapsule5/DATACAPSULE5_PACKAGE_RESULT.json`
- `public_launch/datacapsule5/DATACAPSULE5_NEXT_STEPS.md`
- `public_launch/datacapsule5/DATACAPSULE_CLAIM_BOUNDARY_AUDIT.json`

## Boundary

DataCapsule-5 uses fake local fixtures only. It does not crawl directories, fetch URLs, inspect private data, prove legal sufficiency, certify privacy compliance, guarantee data quality, prove evaluation cleanliness, clear licenses, or authorize actions.
