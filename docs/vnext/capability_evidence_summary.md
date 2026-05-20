# Capability Evidence Summary

`CapabilityEvidenceSummary` describes local evidence available for a capability candidate.

It records:

- official source count
- source trace count
- source trace coverage
- docs/pricing/policy/repository/license/examples presence
- evidence status
- confidence
- evidence notes

Evidence status can be:

- `NO_TRACE`
- `PARTIAL_TRACE`
- `SOURCE_TRACED`
- `OFFICIAL_TRACE_AVAILABLE`
- `STALE_OR_INCOMPLETE`

Source-traced metadata supports a field. It does not prove total correctness, safety, security, or quality.
