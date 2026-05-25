# ROE-4 Public / Private Distribution Split

ROE-4 aligns the current ResidualOps distribution surface after QIRA-9, AgentSec-8, and DataCapsule-7.

Those three packages expose opt-in workflow artifact templates. ROE-4 makes the portfolio distribution rule explicit: public artifacts can help agents and developers use the tools, while private kernel details remain non-public.

## Public Surface

- schemas and artifact shapes
- endpoint or workflow template shapes
- high-level packet, manifest, capsule, residual, receipt, and ALLOW/HOLD/BLOCK language
- public-safe fake fixture summaries
- local negative-control summaries
- claim boundaries and limitations
- opt-in workflow artifact examples under `examples/`

## Private Surface

- private ranking calibration values
- threshold policy
- anti-gaming policy details
- provider trust priors
- private negative-control banks
- private probe seeds
- private receipt weighting
- commercial routing policy
- enterprise data policy
- partner-specific strategy

## Command

```bash
python -m ai_objective_index.residualops_distribution_gate
python -m ai_objective_index.residualops_distribution_gate --audit-only
```

## Boundary

ROE-4 does not enable workflows, call GitHub APIs, post comments, crawl, call live MCP servers, execute external tools, upload packages, submit registry metadata, request tokens, expose private kernels, certify security, guarantee quality, prove product readiness, prove legal/privacy/license/evaluation status, provide purchasing advice, or authorize actions.
