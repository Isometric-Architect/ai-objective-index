# ROE-2 Vertical Status Dashboard

Decision: `PASS_ROE2_DASHBOARD_READY`

ROE-2 is a local read-only dashboard over existing QIRA, AgentSec, and DataCapsule artifacts.

| Vertical | Package | Status | Primary Decision | Artifacts |
| --- | --- | --- | --- | --- |
| QIRA-Code ReleaseGate | QIRA-8 | `ALLOW_OR_PASS` | `PASS_QIRA8_REVIEWER_BUNDLE` | 6 |
| AgentSec Gate | AgentSec-5 | `ALLOW_OR_PASS` | `PASS_AGENTSEC5_FIXTURE_CORPUS_AND_NEGATIVE_CONTROLS` | 7 |
| DataCapsule / AIDREG Engine | DataCapsule-4 | `BLOCK_RISK` | `BLOCK_DATACAPSULE3_USE_RISK` | 6 |

## Portfolio Note

QIRA and AgentSec currently pass their package-level local gates; DataCapsule intentionally retains conservative BLOCK signals in sample use-risk fixtures.

## Boundary

This dashboard does not run probes, execute tools, enable workflows, call GitHub APIs, fetch URLs, upload packages, submit MCP Registry metadata, post to communities, request tokens, certify security, guarantee quality, prove product readiness, or authorize actions.
