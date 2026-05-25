# DataCapsule-6 Repository Corpus Audit Bundle

DataCapsule-6 turns local DataCapsule-5 corpus and negative-control outputs into reviewer-facing artifacts:

- corpus audit report
- review comment draft
- artifact manifest with hashes
- bundle result JSON
- next-step note

The package is local and read-only. It does not crawl directories, inspect private file contents, fetch URLs, call external services, post comments, handle tokens, prove rights, certify privacy, guarantee data quality, prove evaluation cleanliness, clear licenses, provide purchasing advice, or authorize actions.

## Inputs

DataCapsule-6 reads DataCapsule-5 public outputs under `public_launch/datacapsule5/`:

- `DATACAPSULE5_FIXTURE_CORPUS.json`
- `DATACAPSULE5_FIXTURE_CORPUS_REPORT.md`
- `DATACAPSULE5_NEGATIVE_CONTROL_RESULT.json`
- `DATACAPSULE5_NEGATIVE_CONTROL_REPORT.md`
- `DATACAPSULE5_PACKAGE_RESULT.json`

The default CLI regenerates the safe local sample before writing DataCapsule-6 outputs.

## Command

```bash
python -m ai_objective_index.datacapsule.repository_audit_bundle --run-sample
```

Use `--no-upstream-sample` to build from existing local DataCapsule-5 files.

## Public Boundary

DataCapsule-6 may summarize repository-supplied metadata, public-safe fixture outcomes, false-pass counts, and route labels such as `ALLOW_USE`, `HOLD_*`, and `BLOCK_*`.

DataCapsule-6 must not expose exact private scoring policy, receipt weighting, private negative-control banks, private probe seeds, commercial data strategy, hidden rights analysis, or private operational datasets.
