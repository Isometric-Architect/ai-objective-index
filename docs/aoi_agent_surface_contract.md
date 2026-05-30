# AOI Agent Surface Contract

AOI's agent-facing surface follows a three-part rule:

1. Discover first.
2. Preflight second.
3. Carry the claim boundary always.

## Discover Contract

Discover mode returns:

- `objective`
- `mode`
- `top_candidates`
- `best_current_candidate`
- `source_traces`
- `missing_fields`
- `preliminary_route_decision`
- `next_action`
- `must_not_claim`
- `residualops_escalation`
- `freshness`

It may return an all-HOLD candidate set. That is still useful: the response tells the agent what to inspect or request next.

## Preflight Contract

Preflight mode returns:

- `candidate_id`
- `intended_use`
- `route_decision`
- `reason`
- `missing_fields`
- `allowed_next_steps`
- `forbidden_next_steps`
- `must_not_claim`
- `residualops_escalation`
- `claim_ceiling`
- `freshness`

Preflight blocks external action requests, certification/product-readiness claims, secret-like metadata, and private-data use. Missing permission, privacy, retention, policy, pricing, or freshness data should become HOLD with a next action.

## ResidualOps Escalation

- Tool or manifest risk: AgentSec.
- Code or release risk: QIRA.
- Data, corpus, rights, privacy, or eval-boundary risk: DataCapsule.
- Enterprise receipt tracking: ResidualOps dashboard.

No route decision is action authorization.
