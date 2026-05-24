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

Both are deterministic and conservative. They support local review prioritization only, not verification, security certification, quality guarantee, production readiness, or external action authorization.
