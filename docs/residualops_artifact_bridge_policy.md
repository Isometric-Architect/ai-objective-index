# ResidualOps Artifact Bridge Policy

Artifact bridges turn repository-supplied metadata into local review artifacts. They are reusable surfaces, not active automation by default.

Current bridge pattern:

- QIRA: CI evidence and reviewer artifact bundles
- AgentSec: MCP/tool manifest policy-gate artifacts
- DataCapsule: corpus manifest and data-use boundary artifacts

Safe bridge rules:

- keep workflows inactive unless a repository owner opts in
- do not call GitHub APIs by default
- do not fetch URLs
- do not execute external tools
- do not request or store tokens
- do not certify security, quality, rights, privacy, evaluation cleanliness, or product readiness
- do not authorize external actions

The public bridge may expose artifact shape and claim boundaries. Private calibration, private negative controls, anti-gaming rules, provider priors, and commercial routing policy stay non-public.
