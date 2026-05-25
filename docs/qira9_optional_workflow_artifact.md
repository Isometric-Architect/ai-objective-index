# QIRA-9 Optional Workflow Artifact

QIRA-9 packages an opt-in GitHub Actions workflow template for producing local QIRA review artifacts from repository-owned CI evidence.

It does not create an active workflow under `.github/workflows/`. The example remains in `examples/` until a repository owner deliberately copies or adapts it.

## What It Adds

- `examples/qira9_optional_pr_review_artifact_workflow.yml`
- `public_launch/qira9/QIRA9_OPTIONAL_WORKFLOW_RESULT.json`
- `public_launch/qira9/QIRA9_WORKFLOW_AUDIT.json`
- `public_launch/qira9/QIRA9_CLAIM_BOUNDARY_AUDIT.json`
- `public_launch/qira9/QIRA9_ARTIFACT_MANIFEST.json`
- `public_launch/qira9/QIRA9_OPERATOR_RUNBOOK.md`

Run:

```powershell
python -m ai_objective_index.qira.optional_workflow_artifact
python -m ai_objective_index.qira.optional_workflow_artifact --audit-only
```

## Boundary

QIRA-9 is a template and audit package. It does not post comments, call GitHub APIs on behalf of QIRA, apply patches, merge, deploy, upload packages, publish registry metadata, handle tokens, certify security, guarantee quality, prove product readiness, or grant authorization for external actions.

Private thresholds, anti-gaming rules, private negative-control banks, private probe seeds, and commercial policy stay outside public artifacts.
