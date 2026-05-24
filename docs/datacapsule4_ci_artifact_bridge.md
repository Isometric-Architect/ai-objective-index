# DataCapsule-4 CI Artifact Bridge

DataCapsule-4 adds an opt-in CI artifact bridge for repository-supplied corpus manifests. It converts a committed CSV, JSONL, or JSON manifest into local DataCapsule artifacts using the DataCapsule-3 intake path.

The bridge is intentionally inactive by default. The reusable composite action lives at:

`.github/actions/datacapsule-corpus-manifest-artifact/action.yml`

The example workflow lives at:

`examples/datacapsule_corpus_manifest_artifact_workflow.yml`

No active workflow is created under `.github/workflows/`.

## Run Locally

```bash
python -m ai_objective_index.datacapsule.ci_artifact_bridge --run-sample
python -m ai_objective_index.datacapsule.ci_artifact_bridge --audit-manifest
python -m ai_objective_index.datacapsule_claim_audit
```

## Boundaries

DataCapsule-4 does not crawl directories, read private file contents, fetch URLs, call GitHub APIs, post comments, upload artifacts, handle tokens, prove legal sufficiency, prove privacy compliance, guarantee data quality, prove evaluation cleanliness, or authorize actions.

A bridge pass means only that the repository-supplied manifest was converted into local review artifacts without local policy blocks. It is not rights clearance, privacy certification, quality assurance, evaluation-contamination proof, product readiness, or action authorization.
