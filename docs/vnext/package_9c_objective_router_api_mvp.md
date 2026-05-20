# Package 9C Objective Router API MVP

Package 9C exposes the Package 9B Capability Trust model through read-only REST and MCP surfaces.

It adds:

- `POST /v1/objectives/route`
- `POST /v1/objectives/trust-report`
- `GET /v1/capabilities/{capability_id}/trust`
- `GET /v1/objectives/router/status`
- MCP tools: `route_objective`, `get_capability_trust`, `explain_route_decision`
- a separate vNext OpenAPI file at `api/vnext/objective_router_openapi.json`

The router reuses Package 9B trust cards and route decisions. It does not run probes, execute tools, perform gateway actions, fetch live URLs, upload packages, submit MCP Registry metadata, or post to communities.

Route labels are route decisions, not final truth. `ALLOW_CANDIDATE` and `ALLOW_WITH_LIMITS` do not mean verified, safe, security certified, quality guaranteed, product ready, or purchase ready.
