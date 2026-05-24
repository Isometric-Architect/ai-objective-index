# DataCapsule-1 Local Capsule

DataCapsule-1 converts repository-supplied dataset or corpus metadata into a local use-boundary capsule.

It records:

- data ID and name;
- source records;
- license metadata;
- privacy level;
- transform chain;
- risk flags;
- use boundaries for `train`, `retrieve`, `evaluate`, `summarize`, `share`, and `act`.

Run the sample:

```powershell
python -m ai_objective_index.datacapsule.cli_demo --run-sample
```

Outputs are written under `public_launch/datacapsule1/`.

DataCapsule-1 is local metadata review only. It does not crawl, fetch URLs, inspect private data, call external services, certify rights, certify privacy, guarantee data quality, prove evaluation cleanliness, or authorize actions.
