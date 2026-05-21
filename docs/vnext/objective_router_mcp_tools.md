# Objective Router MCP Tools

Package 9C adds three read-only MCP tools.

Package 9D adds receipt-memory MCP tools for local/offline outcome records:

- `submit_execution_receipt`
- `get_execution_receipt`
- `list_capability_receipts`
- `get_capability_receipt_memory`
- `route_objective_with_receipts`

These tools do not run probes or external actions. Receipt memory can warn or downgrade, but it cannot verify a capability or authorize any external action.

## `route_objective`

Routes an objective to local capability candidates and returns an `ObjectiveRouteResponse`.

Inputs:

- `query`
- `objective`
- `domain`
- `data_scope`
- `limit`
- `constraints`

## `get_capability_trust`

Fetches one local `CapabilityTrustCard` by `capability_id`.

## `explain_route_decision`

Returns a compact explanation for one route decision:

- decision
- reason
- claim ceiling
- evidence summary
- risk boundary
- missing fields
- must-not-claim terms

All tools are read-only. They do not fetch network data, run probes, execute external tools, or perform payment, booking, login, email, purchase, form submission, or contract actions.
