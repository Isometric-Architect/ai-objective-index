# Probe-before-Use

The vNext probe loop is:

1. Route an objective to capability candidates.
2. Build a local probe plan for those candidates.
3. Run deterministic metadata probes and negative controls.
4. Store a local probe receipt.
5. Overlay probe warnings or downgrades on the route response.

Probes can add warnings, keep HOLD decisions, or downgrade routes to HOLD/BLOCK. They cannot upgrade HOLD to ALLOW and cannot certify a capability.
