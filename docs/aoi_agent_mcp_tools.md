# AOI Agent MCP Tools

AOI-AGENT-ADOPTION-2 wires read-only MCP tool functions for the agent-native discovery pack:

- `get_aoi_capability_card`
- `discover_capabilities_for_objective`
- `preflight_capability_for_use`
- `explain_aoi_agent_use`
- `list_aoi_agent_examples`

The tools reuse local deterministic helpers. They are designed for ordinary AI agents that need useful source-traced candidates while preserving missing fields, HOLD/BLOCK reasons, freshness/staleness notes, must-not-claim boundaries, and ResidualOps escalation.

## Boundaries

The MCP tools do not call live MCP servers, execute external tools, call external APIs, call GitHub APIs, post comments, create issues, merge, deploy, publish, upload, train, use credentials, certify security, prove correctness, guarantee quality, claim product readiness, or authorize action.

Tool availability is not tool authorization. A listed candidate is not verified. Source traces support fields; they are not proof of total correctness.
