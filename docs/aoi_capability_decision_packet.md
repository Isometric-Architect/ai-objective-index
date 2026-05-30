# AOI Capability Decision Packet

The Capability Decision Packet is the next hardening target for AOI.

It packages a candidate's objective fit, source traces, metadata completeness, freshness, route decision, missing fields, safe next action, blocked next actions, escalation path, and must-not-claim boundary into a machine-readable receipt.

The packet exists because ordinary agents can confuse these states:

- discovered
- trusted
- authorized
- executable

AOI should keep those states separate. A found candidate is not automatically trusted. A trusted candidate is not automatically authorized. An authorized read-only path is not automatically executable for external action.

The packet must not expose private ranking weights, thresholds, provider priors, anti-gaming details, private negative controls, private probe seeds, commercial routing policy, real feedback memory, or customer data.
