# ROE-5 Repository Pilot Checklist

Owner consent gate: `HOLD_OWNER_CONSENT_REQUIRED_BEFORE_ENABLEMENT`

Use this checklist before enabling any ResidualOps workflow in an external or separate repository.

| Rank | Vertical | Package | Example Workflow | Fit |
| --- | --- | --- | --- | --- |
| 1 | AgentSec Gate | `AgentSec-8` | `examples/agentsec8_optional_pr_review_artifact_workflow.yml` | best first external security-facing pilot if repository has MCP/tool manifests |
| 2 | QIRA-Code ReleaseGate | `QIRA-9` | `examples/qira9_optional_pr_review_artifact_workflow.yml` | fastest developer workflow pilot if repository has stable tests and PR packets |
| 3 | DataCapsule / AIDREG Engine | `DataCapsule-7` | `examples/datacapsule7_repository_manifest_workflow.yml` | best data governance pilot if repository has corpus manifests |

## Consent

- Confirm the repository owner wants exactly one workflow enabled for the first pilot.
- Keep first runs manual through `workflow_dispatch`.
- Do not paste tokens into chat, docs, issue text, workflow files, or manifests.

## Repository Inputs

- AgentSec: committed MCP/tool manifest JSON or manifest set.
- QIRA: committed QIRA task packet and repository-owned CI evidence metadata.
- DataCapsule: committed CSV, JSONL, or JSON corpus manifest.

## Review

- Download the generated artifact.
- Review HOLD/BLOCK findings before using any result.
- Treat the artifact as a local review aid, not as verification, certification, product-readiness proof, legal/privacy/license/evaluation proof, purchasing advice, or authorization for actions.
