# DataCapsule-2 Local Corpus Manifest

DataCapsule-2 extends DataCapsule-1 from one metadata object to a repository-supplied corpus manifest. The manifest lists local file paths, source labels, license labels, privacy levels, intended use classes, and risk flags. The builder aggregates that manifest into a local DataCapsule and a corpus report.

It remains local metadata processing only. It does not crawl directories, read private file contents, fetch URLs, call external services, prove legal sufficiency, prove privacy compliance, guarantee data quality, prove evaluation cleanliness, or authorize actions.

Run the sample:

```bash
python -m ai_objective_index.datacapsule.corpus_manifest --run-sample
python -m ai_objective_index.datacapsule_claim_audit
```

The sample writes:

- `public_launch/datacapsule2/DATACAPSULE2_SAMPLE_CORPUS_MANIFEST.json`
- `public_launch/datacapsule2/DATACAPSULE2_CORPUS_CAPSULE.json`
- `public_launch/datacapsule2/DATACAPSULE2_RESULT.json`
- `public_launch/datacapsule2/DATACAPSULE2_REPORT.md`
- `public_launch/datacapsule2/DATACAPSULE2_NEGATIVE_CONTROL_RESULT.json`

## Manifest Shape

The public-safe manifest shape is intentionally small:

```json
{
  "corpus_id": "fixture.local/example-corpus",
  "name": "Example local corpus",
  "root_path": "docs/",
  "source": "repository-local-manifest",
  "allowed_use": {
    "train": false,
    "retrieve": true,
    "evaluate": false,
    "summarize": true,
    "share": false,
    "act": false
  },
  "files": [
    {
      "path": "docs/example.md",
      "source": "repository-local-doc",
      "license": "MIT",
      "privacy_level": "public_metadata",
      "purpose": ["retrieve", "summarize"]
    }
  ]
}
```

## Decision Boundary

DataCapsule-2 can produce `ALLOW_USE`, `HOLD_*`, or `BLOCK_*` use-boundary labels. Those labels are routing aids for local metadata review. They are not legal, privacy, security, quality, product, procurement, or action authorization claims.
