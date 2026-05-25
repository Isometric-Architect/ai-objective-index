# DataCapsule-7 Optional Workflow Artifact

DataCapsule-7 adds a repository-owner opt-in workflow artifact template for DataCapsule local corpus manifest review.

The template stays in `examples/`. It is not copied into `.github/workflows/` by this package and is not active by default.

## What It Does

- accepts a repository-supplied CSV, JSONL, or JSON corpus manifest path through `workflow_dispatch`
- runs the existing DataCapsule corpus manifest artifact composite action
- writes local review artifacts into a workflow artifact directory
- uploads those artifacts with `actions/upload-artifact`

## What It Does Not Do

- no automatic workflow enablement
- no GitHub API calls by DataCapsule
- no review comment posting
- no crawling
- no private file-content inspection
- no URL fetching
- no external service call
- no token handling
- no legal sufficiency claim
- no privacy certification
- no data quality guarantee
- no license clearance
- no evaluation-clean proof
- no purchasing advice
- no authorization for actions

## Command

```bash
python -m ai_objective_index.datacapsule.optional_workflow_artifact
python -m ai_objective_index.datacapsule.optional_workflow_artifact --audit-only
```

## Public Boundary

DataCapsule-7 may expose endpoint shape, manifest fields, local artifact paths, ALLOW/HOLD/BLOCK-style metadata review labels, missing fields, and claim boundaries.

It must not expose private rights analysis, exact receipt weighting, private negative-control banks, private probe seeds, commercial data policy, enterprise data policy, or hidden data acquisition strategy.
