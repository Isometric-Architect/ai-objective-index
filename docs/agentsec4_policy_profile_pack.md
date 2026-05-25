# AgentSec-4 Policy Profile Pack

AgentSec-4 adds a public-safe profile pack for local MCP/tool metadata review.

Profiles include:

- local metadata only
- developer default
- CI artifact review
- MCP Registry metadata review
- strict enterprise

The public profile pack exposes boolean policy shape only. It does not expose exact risk weights, thresholds, provider trust priors, anti-gaming rules, private negative-control seeds, or commercial routing policy.

Run:

```powershell
python -m ai_objective_index.agentsec.profile_pack --write-sample
```

The profile pack does not call live MCP servers, execute tools, fetch URLs, request tokens, certify security, guarantee quality, prove product readiness, or authorize actions.
