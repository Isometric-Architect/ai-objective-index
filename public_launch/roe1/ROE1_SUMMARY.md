# ROE-1 Surface Alignment Summary

Decision: `PASS_ROE1_SURFACE_ALIGNED`

ROE-1 aligns the current QIRA, AgentSec, and DataCapsule public surfaces under the same ResidualOps operating shape: packet or manifest intake, local check/probe/review, receipt/result artifact, ALLOW/HOLD/BLOCK decision, opt-in artifact bridge, and explicit claim boundary.

| Vertical | Packages | Public Role |
| --- | --- | --- |
| QIRA-Code ReleaseGate | QIRA-1, QIRA-2, QIRA-3, QIRA-4, QIRA-5, QIRA-6, QIRA-7, QIRA-8 | AI-generated code and patch release-gate review using local packets, receipts, and artifact bundles. |
| AgentSec Gate | AgentSec-1, AgentSec-2, AgentSec-3 | Local MCP/tool manifest risk review with policy-gate artifacts and explicit action boundaries. |
| DataCapsule / AIDREG Engine | DataCapsule-1, DataCapsule-2, DataCapsule-3, DataCapsule-4 | Local data-use boundary capsules over repository-supplied corpus manifests and eval-separation signals. |

## Boundary

ROE-1 performs local repository checks only. It does not upload packages, submit MCP Registry metadata, enable GitHub workflows, call GitHub APIs, fetch URLs, execute external tools, request tokens, claim verification, certify security, guarantee quality, prove product readiness, or authorize actions. It does not enable workflows.
