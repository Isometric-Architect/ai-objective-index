# ResidualOps External Pilot Runbook

Use this runbook only after ROE-5 produces a PASS onboarding kit.

## Pilot Rules

1. Choose exactly one vertical for the first external repository pilot.
2. Record repository owner consent outside public artifacts.
3. Copy one reviewed example workflow into the target repository only after consent.
4. Keep the first run manual with `workflow_dispatch`.
5. Download the artifact and review HOLD/BLOCK results with the repository owner.

## Pilot Selection

- AgentSec: use when the repository has MCP/tool manifests.
- QIRA: use when the repository has stable CI and PR/task metadata.
- DataCapsule: use when the repository has corpus manifests.

## Do Not Do

- Do not enable multiple workflows at once.
- Do not add automatic PR comments in the first pilot.
- Do not use GitHub API automation in this kit.
- Do not request, print, store, or commit tokens.
- Do not expose private weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, receipt weighting, or commercial routing policy.

The pilot artifact is a review aid. It is not verification, certification, product-readiness proof, legal/privacy/license/evaluation proof, purchasing advice, or authorization for actions.
