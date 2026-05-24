# DataCapsule-3 CSV/JSONL Manifest Intake

DataCapsule-3 accepts repository-supplied CSV, JSONL, or JSON corpus manifest metadata and normalizes it into the DataCapsule-2 corpus manifest shape. It is meant for local RAG/eval/train corpus bookkeeping where teams already maintain a file list with source, license, privacy level, purpose, and risk flags.

It does not crawl directories, read private file contents, fetch URLs, call external services, prove rights, prove privacy compliance, guarantee data quality, prove evaluation cleanliness, or authorize actions.

Run the sample:

```bash
python -m ai_objective_index.datacapsule.manifest_intake --run-sample
python -m ai_objective_index.datacapsule_claim_audit
```

The sample writes:

- `public_launch/datacapsule3/DATACAPSULE3_SAMPLE_MANIFEST.csv`
- `public_launch/datacapsule3/DATACAPSULE3_SAMPLE_MANIFEST.jsonl`
- `public_launch/datacapsule3/DATACAPSULE3_NORMALIZED_MANIFEST.json`
- `public_launch/datacapsule3/DATACAPSULE3_CORPUS_CAPSULE.json`
- `public_launch/datacapsule3/DATACAPSULE3_CORPUS_RESULT.json`
- `public_launch/datacapsule3/DATACAPSULE3_EVAL_LEAK_SEPARATION_REPORT.json`
- `public_launch/datacapsule3/DATACAPSULE3_RESULT.json`
- `public_launch/datacapsule3/DATACAPSULE3_REPORT.md`

## CSV Columns

Expected columns:

- `path`
- `source`
- `license`
- `privacy_level`
- `purpose`
- `risk_flags`

`purpose` can use comma or semicolon separated values such as `retrieve;summarize`. `risk_flags` can use comma or semicolon separated values such as `eval_leak;prompt_injection`.

## JSONL Rows

Each JSONL row can contain the same fields:

```json
{"path":"docs/eval-set.md","source":"repository-local-eval","license":"MIT","privacy_level":"public_metadata","purpose":["evaluate"]}
```

## Boundary

DataCapsule-3 makes local metadata review easier. It is not a live data governance system, legal opinion, privacy compliance system, data quality guarantee, evaluation-contamination proof, or action authorization layer.
