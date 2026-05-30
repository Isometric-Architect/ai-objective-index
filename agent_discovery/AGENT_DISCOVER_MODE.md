# AOI Agent Discover Mode

Discover mode helps ordinary AI agents find useful source-traced capability candidates quickly. It returns top candidates even when every candidate is HOLD, because HOLD should mean "useful but needs next action," not a dead end.

Each candidate includes source trace references, missing fields, a preliminary route decision, must-not-claim terms, freshness notes, and a ResidualOps escalation path.
