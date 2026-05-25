# ROE-5 Portfolio Onboarding Kit

ROE-5 prepares the first external or separate-repository ResidualOps pilot without enabling any workflow.

It turns the ROE-4 public/private distribution split into an operator-facing onboarding kit:

- vertical selection matrix
- owner consent gate
- repository pilot checklist
- dry-run onboarding plan
- claim-boundary audit
- artifact manifest

## Recommended First Pilot

The default recommendation is AgentSec Gate when the target repository has committed MCP/tool manifests. AgentSec is a good first external pilot because it gives a security-facing review artifact without live MCP calls or external tool execution.

QIRA is a strong first pilot when the repository has stable tests and PR/task packets. DataCapsule is a strong first pilot when the repository already has corpus manifests.

## Command

```bash
python -m ai_objective_index.residualops_onboarding_kit
python -m ai_objective_index.residualops_onboarding_kit --audit-only
```

## Boundary

ROE-5 does not enable workflows, call GitHub APIs, post comments, crawl, call live MCP servers, execute external tools, upload packages, submit registry metadata, request tokens, expose private kernels, certify security, guarantee quality, prove product readiness, prove legal/privacy/license/evaluation status, provide purchasing advice, or authorize actions.
