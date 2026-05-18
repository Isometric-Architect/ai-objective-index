# OpenAI MCP Search/Fetch Examples

Package 7A provides generic read-only `search` and `fetch` wrappers.

## search

Example request:

```json
{
  "tool": "search",
  "arguments": {
    "query": "cheap image generation API",
    "data_scope": "integrated",
    "limit": 5
  }
}
```

Example output shape:

```json
{
  "read_only": true,
  "data_scope": "integrated",
  "results": [
    {
      "object_id": "image_api_fixture",
      "name": "PixelForge API",
      "objective_score": 69.12,
      "status": "EXTRACTED_UNVERIFIED"
    }
  ],
  "limitations": ["not a quality guarantee"]
}
```

## fetch

Example request:

```json
{
  "tool": "fetch",
  "arguments": {
    "object_id": "image_api_fixture",
    "data_scope": "integrated"
  }
}
```

`fetch` returns the local object record, score explanation, source traces, missing fields, limitations, and forbidden actions.

No external action is performed. No URL is crawled or fetched.
