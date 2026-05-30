# HOLD-to-Replan Loop Spec

When AOI returns HOLD, the agent should not stop or silently skip the route decision. It should replan within explicit guards.

## Loop

1. Classify the HOLD reason.
2. If fields are missing, request fields or choose a lower-risk action.
3. If metadata is stale, refresh source traces or use an alternate candidate.
4. If authorization is missing, ask the user or admin, or downgrade to read/draft mode.
5. If tool or manifest risk is present, escalate to AgentSec.
6. If code or release risk is present, escalate to QIRA.
7. If data or use-boundary risk is present, escalate to DataCapsule.
8. If `max_iterations` is reached, return candidate-set HOLD with a concrete next action.

## Loop Guards

- `max_iterations` must be explicit.
- Do not repeat the same candidate unless new evidence is attached.
- Do not perform external action during replan.
- Do not auto-approve a HOLD route.
- Do not treat feedback as external action authorization.
