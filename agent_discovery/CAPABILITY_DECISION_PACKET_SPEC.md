# Capability Decision Packet Spec

The Capability Decision Packet is AOI's canonical agent-facing output object. It separates discovered, trusted, authorized, and executable states while preserving route decision receipts.

Required fields include objective, capability identity, candidate source, objective fit score, source trace status, metadata completeness, freshness status, version pin, last checked timestamp, stale warning, rug-pull diff status, negative cache hit, action level, data boundary, auth scope, current auth context, route decision, route reason codes, missing fields, safe next action, blocked next actions, escalation path, receipt id, decision timestamp, recheck policy, and claim ceiling.

`objective_fit_score` is public/demo fit information only. It does not imply safety, authorization, certification, legal/privacy/license clearance, quality guarantee, or product readiness.
