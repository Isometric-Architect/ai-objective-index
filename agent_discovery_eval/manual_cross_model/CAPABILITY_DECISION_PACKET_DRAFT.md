# Capability Decision Packet Draft

A Capability Decision Packet is a machine-readable receipt that lets an ordinary agent distinguish discovery usefulness from execution readiness.

## Required Fields

- `objective`
- `capability_id`
- `candidate_source`
- `capability_type`
- `objective_fit_score`
- `source_trace_status`
- `metadata_completeness`
- `freshness_status`
- `version_pin`
- `last_checked_at`
- `stale_warning`
- `rugpull_diff_status`
- `known_negative_cache_hit`
- `action_level`
- `data_boundary`
- `auth_scope_required`
- `current_auth_context_known`
- `route_decision`
- `route_reason_codes`
- `missing_fields`
- `safe_next_action`
- `blocked_next_actions`
- `escalation_path`
- `must_not_claim`
- `receipt_id`
- `decision_timestamp`
- `recheck_policy`

## Public/Demo Scoring Boundary

- `objective_fit_score` may use transparent public/demo scoring only.
- Do not expose private ranking weights, thresholds, provider priors, private negative controls, private probe seeds, or commercial routing policy.
- Scores do not imply provider verification, security certification, legal clearance, or product readiness.

## Agent Use

The packet should travel between the planner and tool executor. The planner can compare candidates quickly; the executor receives route decisions, missing fields, blocked next actions, and recheck policy before any attempted use.
