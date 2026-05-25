# AgentSec-5 Manifest Fixture Corpus

AgentSec-5 adds a public-safe fake MCP/tool manifest fixture corpus for local AgentSec regression checks.

The corpus includes:

- metadata-only fixtures expected to remain `ALLOW_METADATA_ONLY`
- permission-scope fixtures expected to `HOLD_REVIEW_REQUIRED`
- hidden-instruction fixtures expected to `HOLD_REVIEW_REQUIRED`
- official-like namespace fixtures expected to `HOLD_REVIEW_REQUIRED`
- unsupported positive-claim fixtures expected to `BLOCK_UNSUPPORTED_CLAIM`
- forbidden action fixtures expected to `BLOCK_FORBIDDEN_ACTION`

Run:

```powershell
python -m ai_objective_index.agentsec.fixture_corpus --write-sample
python -m ai_objective_index.agentsec.package5
```

The fixtures are fake local test objects. They do not include real provider secrets, private ranking weights, private thresholds, provider priors, private negative-control seeds, a live security scanner, security certification, quality guarantee, product-readiness proof, or action authorization.
