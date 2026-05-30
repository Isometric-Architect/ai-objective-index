# AOI HOLD-to-Replan Loop

HOLD should not be a dead end for ordinary agents. It should be a productive replan route.

On HOLD, an agent should classify the reason and choose a bounded next step:

- request missing fields
- downgrade to read-only or draft-only mode
- refresh stale source traces
- choose an alternate candidate
- escalate tool risk to AgentSec
- escalate code or release risk to QIRA
- escalate data or use-boundary risk to DataCapsule

Loop guards:

- set `max_iterations`
- do not repeat the same candidate unless new evidence is attached
- do not perform external action during replan
- do not auto-approve

The loop helps the discover-first path stay useful without granting action authorization.

D5 implements a sample CLI:

```bash
python -m ai_objective_index.agent_adoption.hold_to_replan_loop --sample
```
