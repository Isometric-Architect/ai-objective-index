# ROE-4 Opt-In Workflow Distribution Runbook

ROE-4 describes how to distribute the current ResidualOps workflow artifact templates without enabling them automatically.

| Vertical | Package | Example Workflow | Public Surface |
| --- | --- | --- | --- |
| QIRA-Code ReleaseGate | `QIRA-9` | `examples/qira9_optional_pr_review_artifact_workflow.yml` | opt-in workflow artifact template for local PR/release review |
| AgentSec Gate | `AgentSec-8` | `examples/agentsec8_optional_pr_review_artifact_workflow.yml` | opt-in workflow artifact template for local MCP/tool manifest review |
| DataCapsule / AIDREG Engine | `DataCapsule-7` | `examples/datacapsule7_repository_manifest_workflow.yml` | opt-in workflow artifact template for local corpus manifest review |

## Operator Sequence

1. Review the target vertical's example workflow under `examples/`.
2. Confirm the target repository owner wants the workflow enabled.
3. Copy exactly one reviewed example workflow into `.github/workflows/` in that target repository.
4. Keep the first run manual through `workflow_dispatch`.
5. Download the generated artifact and review HOLD/BLOCK rows before using any result.

## Public / Private Rule

Public artifacts may describe schemas, artifact shapes, high-level components, local fixture summaries, ALLOW/HOLD/BLOCK labels, and claim boundaries.

Private material remains non-public: exact weights, thresholds, anti-gaming rules, provider trust priors, private negative-control banks, private probe seeds, private receipt weighting, commercial routing policy, and enterprise data policy.

## Boundary

ROE-4 does not enable workflows, call GitHub APIs, post comments, crawl, call live MCP servers, execute external tools, upload packages, submit registry metadata, request tokens, expose private kernels, certify security, guarantee quality, prove product readiness, prove legal/privacy/license/evaluation status, provide purchasing advice, or authorize actions.
