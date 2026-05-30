# Pilot Feedback Triage

ROE-18 routes feedback categories to the relevant ResidualOps vertical:

- `security_claim_concern` and `tool_manifest_boundary_concern` route to AgentSec.
- `code_release_boundary_concern` routes to QIRA.
- `privacy_or_license_concern` and `data_boundary_concern` route to DataCapsule.
- confusing claims, dashboard issues, missing verticals, and private-kernel concerns route to the portfolio layer.

Triage can recommend a second-run receipt, owner consent, a fixture candidate, a negative-control candidate, or manual review.

Triage does not create issues, send messages, call APIs, or authorize external action.
