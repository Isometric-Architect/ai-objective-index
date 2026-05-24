# AgentSec-2 Policy Gate

AgentSec-2 extends AgentSec-1 from a single manifest scan to a local multi-manifest policy gate.

It accepts a repository-supplied JSON manifest, a JSON list of manifests, or a directory of JSON manifests. Each manifest becomes a `ToolRiskPacket`, then a public-safe `AgentSecPolicyProfile` applies conservative review boundaries.

The default public profile can:

- allow metadata-only review when no blocking or review indicators are found;
- hold tools with network, file, write, secret, browser, code-execution, hidden-instruction, or namespace review indicators;
- block tools that contain forbidden real-world action language;
- block unsupported verification, safety, certification, quality, or product-readiness claims.

Run the sample:

```powershell
python -m ai_objective_index.agentsec.policy_cli --run-sample
```

Outputs are written under `public_launch/agentsec2/`.

AgentSec-2 remains local metadata analysis. It does not call live MCP servers, execute tools, fetch URLs, handle tokens, certify security, guarantee quality, claim product readiness, or authorize external actions.
