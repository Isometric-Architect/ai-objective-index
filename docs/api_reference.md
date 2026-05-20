# API Reference

AOI Package 3 provides a read-only FastAPI REST API over the local Package 0 sample records and Package 1/2 engine functions.

All results are sample or extracted benchmark records. AOI output is not a quality guarantee and is not legal, financial, medical, purchasing, procurement, compliance, or professional advice.

## Run Locally

```powershell
python -m ai_objective_index.api
```

If `uvicorn` is installed, this starts the API on `127.0.0.1:8000`. If it is not installed, use the TestClient tests or install uvicorn.

## Export OpenAPI

```powershell
python -m ai_objective_index.openapi_export
```

This writes `api/openapi.json`.

## Endpoints

### GET /status

Returns service metadata, object count, source trace count, read-only status, and forbidden actions.

### GET /search

Query parameters:

- `query`: required string
- `domain`: optional string
- `objective`: optional string
- `limit`: integer, default `10`

Example:

```text
GET /search?query=cheap%20image%20generation%20API&objective=low%20cost%20commercial%20use
```

Example response shape:

```json
{
  "read_only": true,
  "query": "cheap image generation API",
  "objective": "low cost commercial use",
  "results": [
    {
      "object_id": "aoi-pixelforge-api",
      "name": "PixelForge API",
      "objective_score": 61.0,
      "rank_reason": ["Partial relevance to the stated objective."],
      "missing_fields": ["refund_policy", "enterprise_sla"]
    }
  ],
  "limitations": ["not a quality guarantee"],
  "forbidden_actions": ["payment", "booking", "login"]
}
```

### GET /objects/{object_id}

Returns the full local object record. Unknown objects return:

```json
{
  "error": "object_not_found",
  "object_id": "aoi-example",
  "message": "No object found for object_id."
}
```

### POST /rank

Ranks supplied option names against an objective. Unknown options are scored conservatively and are not crawled.

### POST /compare

Example request:

```json
{
  "object_ids": ["aoi-pixelforge-api", "aoi-motioncanvas-ai"],
  "compare_fields": ["pricing", "docs", "policies", "status"]
}
```

Returns `comparison_table`, `best_for`, `missing_fields_summary`, `warnings`, and `score_summary`.

### GET /objects/{object_id}/score

Returns score components, penalties, rank reasons, warnings, and source trace identifiers.

### GET /objects/{object_id}/source-trace

Optional query parameter:

- `field`: optional field filter

Returns source traces with field, URL, title, snippet, retrieval time, and confidence.

### GET /objects/{object_id}/missing-fields

Returns missing fields with why-it-matters guidance, recommended source, and severity.

### POST /decision-receipt

Example request:

```json
{
  "query": "cheap image generation API with commercial use terms",
  "selected_object_id": "aoi-pixelforge-api",
  "alternatives": ["aoi-motioncanvas-ai"],
  "constraints": {
    "budget_max": 50
  }
}
```

Returns a read-only decision receipt with known limits:

- `v0.1 read-only benchmark output`
- `not a quality guarantee`
- `verify source traces before production use`
- `no purchase, booking, payment, login, email, or contract execution`

### GET /openapi.json

Returns `app.openapi()`.

## Package 6C data_scope

Package 6C adds optional `data_scope` support while preserving the default `sample` behavior. Package 6D hardens and documents that path for beta readiness.

Allowed values:

- `sample`: Package 0/1 sample records only
- `generated`: Package 6A generated fixture extraction records only
- `integrated`: sample + generated records
- `curated`: manually curated candidate records only
- `public_beta`: curated records that pass the Package 7C evidence gate
- `mcp_registry`: Official MCP Registry-style metadata records from local registry intake outputs
- `public_beta_mcp`: registry records that pass the Package 7F calibrated candidate gate

Supported read-only endpoints include:

- `GET /search?query=ocr%20api&data_scope=integrated`
- `GET /search?query=ocr%20api&data_scope=curated`
- `GET /search?query=ocr%20api&data_scope=public_beta`
- `GET /search?query=browser%20automation%20mcp&data_scope=mcp_registry`
- `GET /search?query=browser%20automation%20mcp&data_scope=public_beta_mcp`
- `GET /objects/{object_id}?data_scope=generated`
- `GET /objects/{object_id}/score?data_scope=integrated`
- `GET /objects/{object_id}/source-trace?data_scope=integrated`
- `GET /objects/{object_id}/missing-fields?data_scope=integrated`

POST bodies for `/rank`, `/compare`, and `/decision-receipt` may include `"data_scope": "sample|generated|integrated|curated|public_beta|mcp_registry|public_beta_mcp"`.

Generated, curated, and MCP Registry records remain `EXTRACTED_UNVERIFIED` and are not verified supplier claims. `public_beta` is curated-only by default; `public_beta_mcp` is registry-only by default and means registry metadata candidate, not verified object. If no object passes the relevant evidence gate, the API returns a warning rather than falling back to fake sample data.

`GET /status` reports `sample_object_count`, `generated_object_count`, `integrated_object_count`, `curated_object_count`, `public_beta_object_count`, `mcp_registry_object_count`, `public_beta_mcp_object_count`, `public_beta_mcp_definition`, `default_data_scope`, `read_only`, `live_network_enabled`, and `productization_mode`.

## Package 6D-S Governance Metadata

Package 6D-S extends read-only outputs where safe with:

- `claim_ceiling`;
- `not_asserted`;
- `obstructions`;
- `use_rights`;
- `action_boundary`.

These fields do not change the API into an action system. A recommendation or decision receipt is not permission to buy, book, pay, log in, email, submit forms, connect accounts, purchase, or sign contracts.

## Non-Goals

The API does not crawl URLs, execute purchases, payments, bookings, logins, email sending, form submissions, account connections, supplier claim/verify workflows, profile modifications, or contract signing.

Package 7A MCP `search`/`fetch` wrappers are MCP compatibility tools, not new REST endpoints.

## Package 9C Objective Router API

Package 9C adds read-only vNext router endpoints:

- `POST /v1/objectives/route`
- `POST /v1/objectives/trust-report`
- `GET /v1/capabilities/{capability_id}/trust`
- `GET /v1/objectives/router/status`

These endpoints return route decisions from the vNext Capability Trust model. They do not run probes, execute tools, fetch live URLs, perform gateway actions, upload packages, submit MCP Registry metadata, or post to communities.

`ALLOW_CANDIDATE` and `ALLOW_WITH_LIMITS` mean the candidate can be compared or considered under stated limits. They do not mean verified, safe, security certified, quality guaranteed, product ready, or purchase ready.

The separate vNext OpenAPI file is `api/vnext/objective_router_openapi.json`.
