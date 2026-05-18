# Generated Data Status

Generated AOI data uses conservative status labels.

## Status Taxonomy

- `DISCOVERED`: a potential object was found but not extracted.
- `EXTRACTED`: fields were extracted, but verification status is not yet settled.
- `EXTRACTED_UNVERIFIED`: fields were extracted from local fixture or source text and should be treated as unverified.
- `VERIFIED`: a future status for records that have passed explicit verification. Package 6C does not assign this status.

## Package 6C Generated Fixture Data

Generated fixture data is not supplier-verified. It is local extraction output that can be used for tests, evals, API/MCP integration checks, and report generation.

## Trace And Confidence Requirements

Generated records should include:

- source URLs;
- source traces;
- confidence values;
- missing-field signals.

A source trace supports a field, but it does not guarantee completeness, currentness, legal sufficiency, purchasing suitability, or product quality.

## Missing Fields Are Normal

Missing fields are expected in generated data. AOI surfaces them so ranking and comparison outputs remain cautious.
