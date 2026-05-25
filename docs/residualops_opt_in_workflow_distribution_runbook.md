# ResidualOps Opt-In Workflow Distribution Runbook

This runbook describes how to distribute ResidualOps workflow artifact templates without turning them on automatically.

## Current Templates

- QIRA-9: `examples/qira9_optional_pr_review_artifact_workflow.yml`
- AgentSec-8: `examples/agentsec8_optional_pr_review_artifact_workflow.yml`
- DataCapsule-7: `examples/datacapsule7_repository_manifest_workflow.yml`

## Operator Steps

1. Pick one vertical and one target repository.
2. Review the example workflow and its package docs.
3. Confirm the repository owner wants the workflow enabled.
4. Copy the reviewed workflow into `.github/workflows/` in the target repository.
5. Keep the first runs manual through `workflow_dispatch`.
6. Download the workflow artifact and review HOLD/BLOCK items.

## Rules

- Do not enable all workflows at once by default.
- Do not add automatic PR comments without a separate token-safe package.
- Do not add tokens, `.env`, `.pypirc`, private kernel inventories, private datasets, or commercial policy files to public repos.
- Keep exact weights, thresholds, provider priors, anti-gaming logic, private negative-control banks, and private probe seeds non-public.

The workflow artifacts are review aids. They do not certify security, guarantee quality, prove product readiness, prove legal/privacy/license/evaluation status, provide purchasing advice, or authorize actions.
