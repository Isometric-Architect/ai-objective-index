# ROE-3 Portfolio Release Notes

Decision: `PASS_ROE3_PORTFOLIO_RELEASE_KIT`

ROE-3 packages the current QIRA, AgentSec, and DataCapsule local artifacts into one public-safe ResidualOps portfolio view.

| Vertical | Package | Primary Decision | Public Role |
| --- | --- | --- | --- |
| QIRA-Code ReleaseGate | QIRA-8 | `PASS_QIRA8_REVIEWER_BUNDLE` | local PR/release review artifact bundle |
| AgentSec Gate | AgentSec-7 | `PASS_AGENTSEC7_REVIEWER_BUNDLE` | local AgentSec reviewer report and PR comment draft artifact |
| DataCapsule / AIDREG Engine | DataCapsule-6 | `PASS_DATACAPSULE6_REPOSITORY_AUDIT_BUNDLE` | local repository corpus audit report and review comment draft artifact |

## What This Adds

- A unified release kit over QIRA-8, AgentSec-7, and DataCapsule-6.
- A public vertical index for comparing the current artifact surfaces.
- An operator handoff for the next productization steps.
- A release artifact manifest for the ROE-3 files themselves.

## Boundary

ROE-3 does not enable workflows, call GitHub APIs, post comments, crawl, call live MCP servers, execute external tools, upload packages, submit registry metadata, request tokens, expose private kernels, certify security, guarantee quality, prove product readiness, prove legal/privacy/license/eval status, or authorize actions.
