# AOI Agent REST API

AOI-AGENT-ADOPTION-2 exposes local read-only REST endpoints for ordinary AI agents that need discovery first and preflight second.

## Endpoints

- `GET /v1/agents/capability-card`: returns the machine-readable AOI capability card.
- `POST /v1/agents/discover`: returns source-traced capability candidates, including HOLD candidates with missing fields and next actions.
- `POST /v1/agents/preflight`: checks a candidate before recommendation or use and returns ALLOW/HOLD/BLOCK routing, claim ceilings, allowed next steps, and forbidden next steps.
- `GET /v1/agents/adoption/status`: reports local surface availability and confirms PyPI upload and MCP Registry publish have not been performed by this package.

These endpoints are local and deterministic. They do not call external APIs, run live MCP/tool calls, fetch URLs, upload data, mutate repositories, handle tokens, certify security, prove correctness, guarantee quality, claim product readiness, or authorize external action.

## Agent Rule

Discover output can identify useful candidates. It does not authorize use. Agents should run preflight before recommending, executing, publishing, deploying, uploading, training, or making strong claims about a candidate.
