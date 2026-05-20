# Capability Risk Boundary

`CapabilityRiskBoundary` records the boundary around a candidate before route labels are assigned.

It tracks:

- allowed use
- hold use
- blocked use
- forbidden actions detected
- unsupported claims detected
- sensitive domain flags
- security, legal, and product claim statuses
- route block reasons

Default claim statuses are `NOT_ASSESSED`. Security, legal, and product readiness are held or blocked only as conservative claim-boundary signals. They are not live security scans or legal review.
