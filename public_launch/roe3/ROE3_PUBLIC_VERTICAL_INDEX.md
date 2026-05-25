# ROE-3 Public Vertical Index

## QIRA-Code ReleaseGate

- Package: `QIRA-8`
- Status: `ALLOW_OR_PASS`
- Primary decision: `PASS_QIRA8_REVIEWER_BUNDLE`
- Public role: local PR/release review artifact bundle
- Primary result: `public_launch/qira8/QIRA8_BUNDLE_RESULT.json`
- Claim audit: `public_launch/qira8/QIRA_CLAIM_BOUNDARY_AUDIT.json`

Limits:

- Local artifact limits apply.

## AgentSec Gate

- Package: `AgentSec-7`
- Status: `ALLOW_OR_PASS`
- Primary decision: `PASS_AGENTSEC7_REVIEWER_BUNDLE`
- Public role: local AgentSec reviewer report and PR comment draft artifact
- Primary result: `public_launch/agentsec7/AGENTSEC7_BUNDLE_RESULT.json`
- Claim audit: `public_launch/agentsec7/AGENTSEC_CLAIM_BOUNDARY_AUDIT.json`

Limits:

- local manifest artifact bundle only
- no live MCP call
- no external tool execution
- no URL fetch
- no GitHub API call
- not verification
- not security certification
- not quality guarantee

## DataCapsule / AIDREG Engine

- Package: `DataCapsule-6`
- Status: `ALLOW_OR_PASS`
- Primary decision: `PASS_DATACAPSULE6_REPOSITORY_AUDIT_BUNDLE`
- Public role: local repository corpus audit report and review comment draft artifact
- Primary result: `public_launch/datacapsule6/DATACAPSULE6_BUNDLE_RESULT.json`
- Claim audit: `public_launch/datacapsule6/DATACAPSULE_CLAIM_BOUNDARY_AUDIT.json`

Limits:

- repository-owned local metadata artifact bundle only
- public-safe fake data-use fixtures only
- local negative controls only
- no crawling
- no live source verification
- no private data inspection
- not legal sufficiency
- not privacy compliance
