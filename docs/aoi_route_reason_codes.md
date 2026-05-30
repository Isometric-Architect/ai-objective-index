# AOI Route Reason Codes

Route reason codes explain why AOI selected a route. They are machine-readable and suitable for ordinary agents that need a replan path.

Examples:

- `OBJECTIVE_MATCH`
- `SOURCE_TRACE_PRESENT`
- `METADATA_INCOMPLETE`
- `PERMISSION_SCOPE_UNKNOWN`
- `STALE_METADATA`
- `RUGPULL_DIFF_SUSPECTED`
- `NEGATIVE_CACHE_HIT`
- `DESTRUCTIVE_ACTION`
- `SECRET_LIKE_INPUT`
- `TOOL_RISK_REQUIRES_AGENTSEC`
- `CODE_RELEASE_REQUIRES_QIRA`
- `DATA_USE_REQUIRES_DATACAPSULE`

Reason codes are not private ranking weights, hidden thresholds, provider priors, or certification evidence.
