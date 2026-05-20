# Objective Router API

The Objective Router API is a read-only vNext surface.

## Route Objective

`POST /v1/objectives/route`

Request:

```json
{
  "query": "browser automation MCP server",
  "objective": "select source-traced MCP candidates",
  "domain": "mcp_servers",
  "data_scope": "public_beta_mcp",
  "limit": 5,
  "constraints": {
    "require_source_trace": true,
    "require_policy_clarity": true
  }
}
```

Response:

- route summary
- candidate cards
- ALLOW/HOLD/BLOCK decision labels
- known limits
- must-not-claim terms

## Trust Report

`POST /v1/objectives/trust-report`

This returns the same read-only route response with full trust cards.

## Capability Trust

`GET /v1/capabilities/{capability_id}/trust?data_scope=sample`

Returns one `CapabilityTrustCard` or a stable `capability_not_found` response.

## Status

`GET /v1/objectives/router/status`

Reports read-only boundaries, supported data scopes, decision labels, and disabled execution flags.
