# AgentSec Policy Profiles

AgentSec policy profiles are public-safe wrappers around local manifest risk packets.

The public repository may include:

- profile names;
- whether the profile holds on broad permission categories;
- whether forbidden action language blocks;
- whether unsupported claim language blocks;
- the no-network, no-live-MCP-call, and no-external-tool-execution boundary.

The public repository must not expose private operational weights, exact enterprise thresholds, provider priors, anti-gaming rules, private negative controls, private probe banks, or commercial routing policy.

AgentSec-2 includes two public-safe profile constructors:

- `developer_default_profile()`
- `strict_enterprise_profile()`

AgentSec-4 adds a profile pack around these constructors and related public-safe presets:

- `agentsec-local-metadata-only`
- `agentsec-developer-default`
- `agentsec-ci-artifact-review`
- `agentsec-mcp-registry-metadata`
- `agentsec-strict-enterprise`

All profiles are deterministic and conservative. They support local review prioritization only, not verification, security certification, quality guarantee, production readiness, live gateway protection, or external action authorization.
