# AOI Agent Preflight Mode

Preflight mode runs before an agent recommends or uses a candidate. It separates `tool_available` from `tool_authorized`, and blocks or holds unsafe action claims.

It should be used before live tool execution, external mutation, publication, deployment, upload, training, or strong claims. Missing permission, privacy, policy, pricing, data-retention, or freshness fields become HOLD with next actions.
