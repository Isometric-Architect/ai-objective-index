# AOI Agent Middleware Contract

AOI can be used in three modes.

Advisory mode: the agent reads AOI route decisions and replans.

Enforced mode: the operator places AOI before the tool executor.

Non-bypassable proxy mode: a tool call must pass AOI final argument preflight before execution.

Agent-facing value:

- faster candidate discovery
- fewer failed calls
- fewer missing-field errors
- lower wasted turns

Operator-facing value:

- audit trace
- policy mapping
- escalation
- receipt

The middleware contract is not security certification, legal/privacy/license clearance, product-readiness proof, quality guarantee, or external action authorization.
