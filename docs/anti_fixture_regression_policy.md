# Anti-Fixture Regression Policy

Fixture data is allowed for tests, demos, and offline development. It must never silently replace a real/manual MCP Registry raw payload.

Rules:

- `mcp_registry_raw_v0_1.json` with real/manual registry records must not be overwritten by fixture export unless `--force-fixture` is explicitly passed.
- Fixture records must not be promoted to `public_beta_mcp`.
- Public beta MCP candidates must come from real/manual or explicit live Official MCP Registry metadata.
- Fixture-only rows must stay visible as `HOLD_FIXTURE_ONLY`.

This policy prevents false closure where fake example records look like public beta data.

