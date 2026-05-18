# OpenAI MCP Compatibility

Package 7A adds generic read-only `search` and `fetch` wrappers for MCP clients that prefer those tool names.

## search

`search(query, data_scope="sample", limit=10)` returns objective-ranked AOI candidates using the existing `search_objectives` implementation.

The wrapper includes:

- `read_only: true`;
- `data_scope`;
- ranked results;
- confidence where available;
- source URLs where available;
- limitations;
- forbidden actions.

## fetch

`fetch(object_id, data_scope="sample")` returns one AOI object with:

- full local object record;
- objective score explanation;
- source traces;
- missing fields;
- status and confidence;
- limitations;
- forbidden actions.

## Boundary

`search` and `fetch` do not crawl the web and do not fetch remote URLs. Results are not quality guarantees, purchasing advice, legal/security/compliance certification, or action permission.
