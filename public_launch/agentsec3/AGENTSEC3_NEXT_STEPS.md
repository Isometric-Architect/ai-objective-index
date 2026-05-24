# AgentSec-3 Next Steps

1. Keep the workflow example in `examples/` until the repository owner opts in.
2. Feed repository-supplied MCP/tool manifests into the bridge from normal CI.
3. Publish AgentSec JSON/Markdown outputs as workflow artifacts only if the repository owner wants them.
4. Keep live proxy behavior, runtime sandboxing, external tool calls, and action authorization separately gated.

AgentSec-3 does not call live MCP servers, execute tools, fetch URLs, call GitHub APIs, post comments, handle tokens, certify security, guarantee quality, claim product readiness, or authorize external actions.
