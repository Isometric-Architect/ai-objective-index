# AOI Agent Preflight

Preflight runs before an agent recommends or uses a candidate. It separates tool availability from tool authorization and blocks external action requests, credential handling, certification claims, and product-readiness claims.

Missing permission, privacy, retention, policy, pricing, or freshness fields produce HOLD with next action.

AOI Agent Discovery 3 tests this behavior with offline ordinary-agent fixtures. The AOI-guided fixture should block execution authorization and unsupported readiness wording while still giving useful next actions for HOLD cases.
