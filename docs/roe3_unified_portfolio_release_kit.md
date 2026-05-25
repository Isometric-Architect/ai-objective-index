# ROE-3 Unified Portfolio Release Kit

ROE-3 packages the current public-safe ResidualOps vertical artifacts into one local portfolio release kit.

Current verticals:

- QIRA-Code ReleaseGate: QIRA-8 reviewer bundle
- AgentSec Gate: AgentSec-7 reviewer bundle
- DataCapsule / AIDREG Engine: DataCapsule-6 repository corpus audit bundle

Run:

```powershell
python -m ai_objective_index.residualops_portfolio_release_kit
python -m ai_objective_index.residualops_portfolio_release_audit
```

## What ROE-3 Produces

- `ROE3_PORTFOLIO_RELEASE_KIT.json`
- `ROE3_PORTFOLIO_RELEASE_NOTES.md`
- `ROE3_PUBLIC_VERTICAL_INDEX.md`
- `ROE3_OPERATOR_HANDOFF.md`
- `ROE3_ARTIFACT_MANIFEST.json`
- `ROE3_CLAIM_BOUNDARY_AUDIT.json`
- `ROE3_NEXT_STEPS.md`

## Boundary

ROE-3 is a local packaging layer only. It does not enable workflows, call GitHub APIs, post comments, crawl, call live MCP servers, execute external tools, upload packages, submit registry metadata, request tokens, expose private kernels, certify security, guarantee quality, prove product readiness, prove legal/privacy/license/evaluation status, or authorize actions.
