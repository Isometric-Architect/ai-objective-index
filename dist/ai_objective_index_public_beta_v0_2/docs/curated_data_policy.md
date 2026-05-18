# Curated Data Policy

Curated AOI data is manually entered candidate data for AI tools, APIs, SaaS products, datasets, services, and MCP servers.

Package 7C is local-data-only:

- no live crawling;
- no scraping;
- no network fetch;
- no external LLM extraction;
- no supplier claim or supplier verification workflow;
- no payment, booking, login, email sending, form submission, purchase, account connection, or contract signing.

## Status

Curated does not mean verified. Curated objects default to `EXTRACTED_UNVERIFIED` and must not become `VERIFIED` or `ACTION_READY` without a future explicit verification flow.

## Source Traces

Every public beta candidate needs at least one source trace. Pricing, docs, commercial-use, policy, license, and rate-limit claims should have field-level traces when those fields are present.

Source traces support fields; they do not prove completeness, currentness, legal sufficiency, product quality, or supplier approval.

## Public Beta Scope

`public_beta` is curated-only by default. It excludes fake sample data and local generated fixture data unless a future explicit flag says otherwise.

If no curated objects pass the evidence gate, `public_beta` should return an empty result with a clear warning.
