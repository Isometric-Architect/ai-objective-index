# Execution Receipt Loop

ExecutionReceipt records what happened after a capability was selected or held.

It includes objective, capability, agent hash, environment class, selected pipeline, outcome, verifier result, negative-control result, latency/cost bucket, error type, residual found, claim ceiling change, and timestamp.

The loop is intended to improve future routing. Package 9A only defines the schema and roadmap; it does not implement a live execution gateway.
