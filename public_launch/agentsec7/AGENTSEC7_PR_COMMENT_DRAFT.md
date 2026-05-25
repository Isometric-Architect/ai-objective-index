## AgentSec Review Draft

Decision: `PASS_AGENTSEC6_LOCAL_MANIFEST_CORPUS_PACKAGE`

- Corpus intake: `PASS_AGENTSEC6_LOCAL_CORPUS_INTAKE`
- Policy gate: `BLOCK_AGENTSEC2_POLICY_RISK`
- Manifests reviewed as local metadata: `5`
- ALLOW metadata-only: `1`
- HOLD review: `2`
- BLOCK policy risk: `2`

This is a draft only. AgentSec did not post this comment, call live MCP servers, execute tools, fetch URLs, call GitHub APIs, handle tokens, certify security, guarantee quality, prove product readiness, or authorize external actions.

Reviewer follow-up:
- Review every HOLD item before use.
- Treat BLOCK items as unsuitable for the requested scope unless the manifest or policy is changed and reviewed again.
- Keep private thresholds, provider priors, anti-gaming rules, and private negative-control banks outside this public artifact.
