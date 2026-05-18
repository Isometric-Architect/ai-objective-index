# MCP Registry Evidence Gate

Package 7D validates MCP Registry intake records before they can appear in `public_beta_mcp`.

## PASS

- `PASS_REGISTRY_CANDIDATE`: object has an id/name, source trace, registry metadata source, `EXTRACTED_UNVERIFIED` status, and enough repository/docs/capability metadata.

## HOLD

- `HOLD_MISSING_REPO`
- `HOLD_MISSING_DOCS`
- `HOLD_WEAK_CAPABILITY`
- `HOLD_FIXTURE_ONLY`

Fixture records are useful for local tests, but they are not promoted to `public_beta_mcp`.

## BLOCK

- `BLOCK_INVALID_URL`
- `BLOCK_FORBIDDEN_STATUS`
- `BLOCK_NO_TRACE`
- `BLOCK_FORBIDDEN_ACTION_CLAIM`

The evidence gate is not a security certification, supplier verification, quality guarantee, or purchase recommendation.

## Package 7F Calibration

Package 7F adds a separate candidate gate for beta display. `PASS_PUBLIC_BETA_CANDIDATE` means a source-traced registry record can appear in `public_beta_mcp` as `REGISTRY_METADATA_CANDIDATE`.

It still does not mean `VERIFIED`, `ACTION_READY`, safe, secure, maintained, high quality, supplier verified, or security certified. Missing pricing or policy fields are HOLD context for MCP metadata rather than automatic blocks.
