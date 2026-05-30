# HOLD-to-Replan Loop Spec

On HOLD, classify the route reason, request missing evidence or downgrade to a lower-risk action, and stop after `max_iterations`.

Rules:

- no external action during replan
- no auto-approval
- no repeated candidate unless new evidence is attached
- escalation routes must identify AgentSec, QIRA, DataCapsule, human approval, or operator policy
