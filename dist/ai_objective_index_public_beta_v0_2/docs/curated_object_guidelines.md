# Curated Object Guidelines

Add curated rows manually in `data/curated/curated_objects_v0_1.jsonl` and matching field traces in `data/curated/curated_source_traces_v0_1.jsonl`.

## Object Rows

Use stable object IDs such as `curated-vendor-product-api`. Include:

- `object_id`
- `name`
- `object_type`
- `summary`
- `official_url`
- `docs_url`, `pricing_url`, `terms_url`, `privacy_url`, or `github_url` when known
- comma-separated `capabilities`, `categories`, and `missing_fields`
- `status`: normally `EXTRACTED_UNVERIFIED`
- `confidence`: `0.0` to `1.0`
- `notes`

Do not mark curated rows as `VERIFIED` or `ACTION_READY`.

## Source Trace Rows

Each trace should include:

- `trace_id`
- `object_id`
- `field`
- `source_url`
- `source_title`
- `source_snippet`
- `retrieved_at`
- `confidence`
- `source_rank`
- `curator_note`

Use official pages for official claims when possible. If a pricing or policy field has no source trace, leave the field missing and add it to `missing_fields`.

## Placeholder Rows

Placeholder rows must use `example.com`, low confidence, and notes such as `placeholder example, not public beta candidate`.
