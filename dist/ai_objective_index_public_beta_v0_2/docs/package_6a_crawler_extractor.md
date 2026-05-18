# Package 6A Crawler / Extractor Skeleton

Package 6A adds a local-first acquisition skeleton for AI Objective Index.

## What It Adds

- Robots policy helper.
- Per-domain rate limiter.
- Optional fetcher with network disabled by default.
- Source cache.
- Sitemap parsing helpers.
- GitHub README URL helpers.
- Crawl plan preview command.
- Rule-based page classification and extraction.
- Source-trace mapping.
- ActionObject builder.
- Fixture pipeline that generates extracted objects and source traces.

## Run Crawl Plan Preview

```powershell
python -m ai_objective_index.crawler.crawl_plan
```

This prints planned seed URLs only. It does not fetch the network.

## Run Fixture Pipeline

```powershell
python -m ai_objective_index.extractor.fixture_pipeline
```

The pipeline reads `data/fixtures/pages/` and writes:

- `data/generated/extracted_objects_v0_2.json`
- `data/generated/extracted_source_traces_v0_2.json`
- `data/generated/extraction_report_v0_2.json`

## Status Boundary

Extracted objects default to `EXTRACTED_UNVERIFIED`. Source traces support fields but do not guarantee correctness, completeness, safety, or purchase readiness.

## Intentionally Not Implemented

- Broad live crawling.
- External LLM extraction.
- REST ingestion endpoints.
- Supplier claim or verification.
- Payment, booking, login, email sending, form submission, purchase, or contract signing.
