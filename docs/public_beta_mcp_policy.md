# Public Beta MCP Policy

`public_beta_mcp` is a beta candidate data scope built from local Official MCP Registry metadata.

It is read-only and local-data-only. It does not fetch external URLs, scrape websites, follow links, call external LLM APIs, submit to registries, or publish anything.

## Claim Boundary

Objects in `public_beta_mcp` are registry metadata candidates:

- not `VERIFIED`;
- not `ACTION_READY`;
- not supplier verified;
- not security certified;
- not a quality guarantee;
- not purchasing advice;
- not action permission.

All objects remain `EXTRACTED_UNVERIFIED` or equivalent. The display status may say `REGISTRY_METADATA_CANDIDATE` to make the beta surface easier to read, but the underlying claim ceiling remains unverified registry metadata.

