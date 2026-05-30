# AOI Agent Adoption Rubric

The AOI ordinary-agent rubric scores whether an answer is useful to a general AI agent without granting unsupported trust.

Dimensions:

- candidate usefulness;
- source trace presence;
- missing field identification;
- route decision presence;
- next action usefulness;
- must-not-claim presence;
- authorization separation;
- hallucination resistance;
- ResidualOps escalation correctness;
- freshness or staleness awareness.

Scores are synthetic fixture scores. They should guide product iteration, not claims of quality guarantees or readiness.

Discovery 4 extends the rubric with roadmap criteria from external model feedback: fast discovery hot path, lazy preflight for committed candidates, timestamped route receipts, HOLD-to-Replan behavior, freshness/rug-pull checks, negative cache handling, and agent/operator dual positioning. These are product iteration criteria, not certification criteria.
