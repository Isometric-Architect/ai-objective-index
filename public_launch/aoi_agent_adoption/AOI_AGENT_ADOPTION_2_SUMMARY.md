# AOI Agent Adoption 2 Summary

Decision: `PASS_AGENT_SURFACES_READY_FOR_030A2_UPLOAD`

AOI-AGENT-ADOPTION-2 wires AOI's ordinary-agent discover/preflight pack into local read-only REST and MCP surfaces for the unpublished `0.3.0a2` package candidate.

| Surface | Status |
| --- | --- |
| REST endpoints | `PASS_REST_AGENT_SURFACE_READY` |
| MCP tools | `PASS_MCP_AGENT_SURFACE_READY` |
| OpenAPI regenerated | `True` |
| MCP manifest regenerated | `True` |
| External APIs used | `False` |
| PyPI upload performed | `False` |
| MCP Registry publish performed | `False` |

The surfaces are local and read-only. They return capability-card, discover, preflight, explanation, and example metadata with missing fields, next actions, must-not-claim boundaries, freshness/staleness signals, and ResidualOps escalation. They do not execute live tools, authorize external action, certify security, prove correctness, guarantee quality, claim product readiness, handle tokens, or expose private kernel values.
