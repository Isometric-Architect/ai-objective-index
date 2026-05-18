# LlamaIndex Integration Notes

This is a lightweight conceptual example. It does not add a LlamaIndex dependency.

## REST Pattern

1. Start the local read-only API:

```bash
python -m ai_objective_index.api
```

2. Use an HTTP tool or custom retriever to call:

```text
GET http://127.0.0.1:8000/search?query=cheap%20image%20generation%20API
```

3. Feed the returned `results`, `rank_reason`, `missing_fields`, and source trace IDs into your LlamaIndex response synthesis step.

## MCP Pattern

When a real MCP runtime is configured, expose AOI through `python -m ai_objective_index.mcp_server` and call read-only tools such as `search_objectives`, `explain_score`, and `get_source_trace`.

AOI does not crawl, purchase, book, log in, send email, submit forms, or sign contracts.

