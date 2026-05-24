# ResidualOps Vertical Surface Matrix

| Vertical | Current Surface | Public Artifact Pattern | Boundary |
| --- | --- | --- | --- |
| QIRA-Code ReleaseGate | QIRA-1 through QIRA-8 | task packet, behavior contract, release-gate report, patch receipt, reviewer artifact bundle | Does not apply patches, run commands, merge, deploy, certify security, guarantee quality, or authorize production use. |
| AgentSec Gate | AgentSec-1 through AgentSec-3 | tool risk packet, manifest scanner, policy-gate result, CI artifact bridge | Does not call live MCP servers, execute tools, fetch URLs, certify security, guarantee quality, or authorize actions. |
| DataCapsule / AIDREG Engine | DataCapsule-1 through DataCapsule-4 | corpus manifest, data-use capsule, eval-separation report, CI artifact bridge | Does not inspect private file contents, crawl, fetch URLs, prove rights/privacy/data quality/eval cleanliness, or authorize actions. |

The shared public shape is:

```text
Packet or manifest
-> local check/probe/review
-> receipt or result artifact
-> ALLOW/HOLD/BLOCK
-> optional artifact bridge
-> claim boundary
```

The public matrix does not include exact weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, commercial routing policy, or private data strategy.
