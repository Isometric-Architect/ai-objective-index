# ROE-1 Surface Alignment Gate

ROE-1 checks that QIRA, AgentSec, and DataCapsule expose compatible public surfaces before the ResidualOps family grows further.

The gate looks for the same public pattern in each vertical:

- packet, manifest, or capsule intake
- local check, probe, or review
- receipt, result, or report artifact
- ALLOW/HOLD/BLOCK decision labels
- opt-in artifact bridge
- explicit claim boundaries

ROE-1 is local repository analysis only. It does not enable GitHub workflows, call GitHub APIs, fetch URLs, execute external tools, upload packages, submit MCP Registry metadata, request tokens, post to communities, certify security, guarantee quality, prove product readiness, or authorize actions.

Run:

```powershell
python -m ai_objective_index.residualops_surface_alignment
python -m ai_objective_index.residualops_public_private_alignment_audit
```

Outputs are written under `public_launch/roe1/`.
