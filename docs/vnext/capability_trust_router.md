# Capability Trust Router

AOI vNext routes AI agents from objectives to capabilities with evidence, residual risk, and usage boundaries.

The public routing vocabulary includes:

- objective fit
- evidence credit
- eco validation
- integration ease
- freshness
- residual risk
- security risk
- context burden
- cost/latency penalty
- claim inflation risk
- failure similarity

The public outcome vocabulary is `ALLOW`, `HOLD`, and `BLOCK`.

Actual weights, thresholds, anti-gaming heuristics, negative-control seeds, and provider trust priors are not public. Public docs explain the axes and receipts, not the private ranking kernel.

This is not a security certification or quality guarantee.

Package 9B implements a minimal offline version of this router vocabulary. The output is a source-traced route-readiness estimate with ALLOW/HOLD/BLOCK labels. It does not override hard risk boundaries, and objective fit cannot convert missing evidence or unsupported claims into verification.
