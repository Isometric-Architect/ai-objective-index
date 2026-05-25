# AgentSec-8 Optional Workflow Artifact

AgentSec-8 packages an opt-in GitHub Actions workflow template for producing local AgentSec review artifacts.

It does not create an active workflow under `.github/workflows/`. The example remains in `examples/` until a repository owner deliberately copies or adapts it.

## What It Adds

- `examples/agentsec8_optional_pr_review_artifact_workflow.yml`
- `public_launch/agentsec8/AGENTSEC8_OPTIONAL_WORKFLOW_RESULT.json`
- `public_launch/agentsec8/AGENTSEC8_WORKFLOW_AUDIT.json`
- `public_launch/agentsec8/AGENTSEC8_CLAIM_BOUNDARY_AUDIT.json`
- `public_launch/agentsec8/AGENTSEC8_ARTIFACT_MANIFEST.json`
- `public_launch/agentsec8/AGENTSEC8_OPERATOR_RUNBOOK.md`

Run:

```powershell
python -m ai_objective_index.agentsec.optional_workflow_artifact
python -m ai_objective_index.agentsec.optional_workflow_artifact --audit-only
```

## Boundary

AgentSec-8 is a template and audit package. It does not post comments, call live MCP servers, execute tools, fetch URLs, call GitHub APIs on behalf of AgentSec, handle tokens, certify security, guarantee quality, prove product readiness, or authorize external actions.

Private weights, thresholds, provider priors, anti-gaming rules, private negative-control banks, private probe seeds, and commercial policy stay outside public artifacts.
