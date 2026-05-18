# Extraction Methodology

Package 6A introduces rule-based extraction over local fixtures. It is designed to make source traces first-class before any future live crawler is enabled.

## Principles

- Extract fields from public text only.
- Prefer official pages such as pricing, docs, terms, privacy, and GitHub README files.
- Every important extracted field should have a `SourceTrace` when possible.
- Automatically extracted objects default to `EXTRACTED_UNVERIFIED`.
- Confidence is a heuristic, not a guarantee.
- Missing fields are surfaced rather than silently filled.

## Rule-Based Extraction

The initial extractor uses keyword rules for:

- free plan and pricing;
- API availability and docs;
- commercial-use language;
- rate limits;
- privacy and terms language;
- MCP support;
- open-source and GitHub references.

These rules are deliberately simple so failures can become explicit eval cases.

## Source Traces

A source trace records:

- object id;
- field;
- source URL;
- source title;
- source snippet;
- retrieval timestamp;
- confidence;
- source rank.

A trace supports a field. It does not prove the field is complete, current, legally sufficient, or safe for production use.

## Missing Fields

Generated objects are passed through the existing `missing_fields` module. This keeps crawler outputs compatible with the Package 1 scoring engine and Package 2/3 read-only interfaces.

