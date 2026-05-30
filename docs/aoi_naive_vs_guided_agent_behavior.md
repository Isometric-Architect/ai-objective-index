# AOI Naive vs Guided Agent Behavior

The naive baseline represents fast but fragile agent behavior: it recommends quickly, accepts untraced candidates, and often skips missing fields or permission boundaries.

The AOI-guided fixture keeps the useful part of discovery while adding pre-use trust routing. It does not merely block. It returns top candidates, explains HOLD, and gives next actions.

Expected improvements:

- fewer accepted hallucinated candidates;
- less overclaim;
- clearer separation between availability and authorization;
- better HOLD handling;
- better ResidualOps escalation for tool, code, and data risk.

This comparison is offline and deterministic. Manual cross-model evaluation is still needed before making broader adoption claims.
