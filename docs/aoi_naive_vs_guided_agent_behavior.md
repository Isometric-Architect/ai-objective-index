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

Discovery 4 records that manual cross-model feedback as local redacted packets and identifies the main upgrade path: make AOI less like a static registry and more like a fast capability finder with pre-use route receipts. The residual generated registry/datascope full-suite failure remains classified as HOLD until a full suite passes.
