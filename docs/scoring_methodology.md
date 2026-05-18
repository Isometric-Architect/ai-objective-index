# Scoring Methodology

AOI v0.1 defines an objective-fit score from 0 to 100. The score explains how well an object appears to match a stated objective and constraints from the available fields and source traces.

The score is not a universal product-quality score. It is not legal, financial, medical, procurement, purchasing, compliance, or professional advice.

Package 4 benchmark scores remain heuristic. They are useful for regression tests, golden-query review, and report generation, but they are not a quality guarantee, official ranking, safety certification, or purchasing recommendation.

## Components

Each component may be scored from 0 to 100 before weighting.

### relevance

How directly the object's type, capabilities, categories, and summary match the requested objective.

### cost_fit

How well pricing appears to fit the stated budget or cost constraints. Unknown pricing should reduce confidence and may add a missing-field penalty.

### policy_clarity

How clear the object's policies are for the objective, including commercial use, data retention, terms, privacy, rate limits, and other stated constraints.

### documentation_quality

How complete and usable the documentation appears to be, including docs URLs, API references, quickstarts, examples, SDK references, and integration notes.

### trust_signal

General confidence signals such as apparent active status, maintained documentation, transparent policy pages, support channels, or open-source repository activity when relevant.

### source_trace_coverage

How much of the ranking-relevant data is supported by source traces. A trace supports a field; it does not guarantee that the source is complete, current, or legally sufficient.

### freshness

How recently the object and traces were checked. Freshness should use `last_checked_at` and `retrieved_at` values once real ingestion exists.

## Penalties

### missing_field_penalty

Applied when ranking-relevant fields are missing, vague, or unsupported. Missing fields should be surfaced in outputs rather than hidden.

### unsafe_claim_penalty

Applied when an output would overclaim beyond AOI boundaries, such as presenting a recommendation as guaranteed quality, official certification, legal advice, purchasing advice, or automatic execution authority.

## Suggested Default Weighting

```json
{
  "relevance": 0.30,
  "cost_fit": 0.15,
  "policy_clarity": 0.15,
  "documentation_quality": 0.15,
  "trust_signal": 0.10,
  "source_trace_coverage": 0.10,
  "freshness": 0.05
}
```

The final score should subtract penalties after the weighted component score is calculated and clamp the result to 0 through 100.

## Output Requirements

Every scored result should include:

- `object_id`;
- `objective_score`;
- component scores;
- penalties;
- `rank_reason`;
- warnings when fields are missing, stale, ambiguous, or weakly traced.

## Package 6D-S Source-Governed Fields

Package 6D-S adds governance metadata to scored results where safe:

- `claim_ceiling`: the highest safe claim tier for the object;
- `obstructions`: HOLD/BLOCK certificates for missing source, policy, price, freshness, validator, use-right, or action-boundary evidence;
- `not_asserted`: explicit statements AOI does not make, including quality guarantees and action permission.

The objective score remains a heuristic fit score. It does not override source status, validator holds, claim ceilings, use-right limits, or action-boundary blocks.
