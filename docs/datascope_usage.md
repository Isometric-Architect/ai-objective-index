# Data Scope Usage

AOI supports seven local data scopes:

- `sample`: default Package 0/1 sample records.
- `generated`: local Package 6A fixture extraction records.
- `integrated`: sample + generated records.
- `curated`: manually curated real-object candidates.
- `public_beta`: curated candidates that pass the evidence gate.
- `mcp_registry`: local Official MCP Registry intake records.
- `public_beta_mcp`: registry records that pass the calibrated registry candidate gate.

The default is always `sample`.

Generated, curated, and MCP Registry data remain `EXTRACTED_UNVERIFIED`. Generated data is source-traced fixture extraction data; curated data is manually entered candidate data; registry data is official-registry-style metadata intake. None of these are supplier-verified data, security certification, live crawl output, or verification claims.

`public_beta` is curated-only by default. It does not include fake sample records or generated fixtures unless a future explicit flag is added.

`public_beta_mcp` is registry-only by default. Package 7F builds it from saved Official MCP Registry metadata as `REGISTRY_METADATA_CANDIDATE` rows. These rows remain `EXTRACTED_UNVERIFIED` and are not verified, security certified, quality guaranteed, or action-ready. In offline fixture mode it may be empty and should return a warning rather than falling back to fake sample data.

Package 6D remains local-only:

- no live crawling;
- no network fetch;
- no external LLM APIs;
- no payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

Productization Mode allows implementation to proceed. Product, public, security, legal, market, or readiness claims still require product evidence.

## REST API

Use `data_scope` as a query parameter:

```text
GET /search?query=cheap%20image%20generation%20API&data_scope=integrated
GET /search?query=cheap%20image%20generation%20API&data_scope=curated
GET /search?query=cheap%20image%20generation%20API&data_scope=public_beta
GET /search?query=browser%20automation%20mcp&data_scope=mcp_registry
GET /search?query=browser%20automation%20mcp&data_scope=public_beta_mcp
GET /objects/image_api_fixture?data_scope=generated
GET /objects/image_api_fixture/score?data_scope=generated
GET /objects/image_api_fixture/source-trace?data_scope=generated
GET /objects/image_api_fixture/missing-fields?data_scope=generated
```

POST endpoints accept `data_scope` in the request body:

```json
{
  "object_ids": ["image_api_fixture", "ocr_api_fixture"],
  "data_scope": "generated"
}
```

## MCP Tools

Read-only MCP helper functions accept `data_scope` where relevant:

- `search_objectives`
- `rank_options`
- `compare_tools`
- `explain_score`
- `get_source_trace`
- `list_missing_fields`
- `generate_decision_receipt`

Default remains `sample`.

## Hugging Face Demo

The local demo exposes a data scope dropdown. The import-safe helper also accepts:

```python
run_demo_query("cheap image generation API", data_scope="integrated")
run_demo_query("cheap image generation API", data_scope="public_beta")
run_demo_query("browser automation MCP", data_scope="mcp_registry")
run_demo_query("browser automation MCP", data_scope="public_beta_mcp")
```
