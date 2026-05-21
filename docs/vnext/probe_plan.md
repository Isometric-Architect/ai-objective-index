# ProbePlan

`ProbePlan` groups local `ProbeCard` checks for a route response.

Allowed execution is `deterministic_local_only`. Forbidden execution includes network calls, live MCP calls, external tools, shell subprocess, payment, booking, login, email, purchase, and contract actions.

The plan output is a `ProbeReceipt` and optional `ProbeRouteOverlay`. A plan is not a gateway policy and not a security certification.
