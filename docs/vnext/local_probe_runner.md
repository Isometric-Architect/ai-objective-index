# Local Probe Runner

The local runner supports:

- source trace integrity checks
- missing field checks
- policy clarity checks
- docs, repository, and license presence checks
- unsupported claim checks
- forbidden action checks
- fixture-only negative controls

The runner uses only local AOI objects, source traces, and missing-field metadata. It does not call live services, run MCP tools, fetch URLs, or execute shell commands.
