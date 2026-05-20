# Capability Trust Card

`CapabilityTrustCard` is the vNext route-readiness record for one capability candidate against one objective.

Important fields:

- `objective_id`: the objective being routed.
- `capability_id` / `object_id`: the candidate capability and source AOI object.
- `integration_type`: `api`, `mcp_server`, `python_package`, `dataset`, `service`, `tool`, `agent`, or `unknown`.
- `source_trace_ids`: source traces used by the local calculation.
- `evidence_summary`: trace coverage and available official metadata.
- `match`: objective-relative fit components.
- `risk_boundary`: forbidden actions, unsupported claims, and review holds.
- `route_decision`: ALLOW/HOLD/BLOCK result.
- `score_components`: deterministic demo components, not objective truth.

The card is not a quality guarantee and not security certification.
