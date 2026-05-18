# Registry Candidate Gate

Package 7F adds a calibrated candidate gate for `public_beta_mcp`.

`PASS_PUBLIC_BETA_CANDIDATE` means an MCP Registry record is useful enough to appear in AOI beta metadata surfaces. It does not mean the server is `VERIFIED`, `ACTION_READY`, safe, maintained, high quality, supplier verified, or security certified.

## Tokens

- `PASS_PUBLIC_BETA_CANDIDATE`: source-traced registry metadata candidate for beta display.
- `HOLD_FIXTURE_ONLY`: local fixture records are useful for tests but not public beta candidates.
- `HOLD_MISSING_DESCRIPTION`: description is absent or too generic.
- `HOLD_MISSING_REPOSITORY`: repository metadata is missing.
- `HOLD_MISSING_PACKAGE`: package, remote, or install metadata is missing.
- `HOLD_WEAK_TRACE`: trace confidence is weak.
- `BLOCK_INVALID_URL`: URL is not HTTP/HTTPS.
- `BLOCK_FORBIDDEN_STATUS`: record tries to become `VERIFIED` or `ACTION_READY`.
- `BLOCK_NO_TRACE`: record has no source trace.
- `BLOCK_SECURITY_CERTIFICATION_CLAIM`: record attempts a security-certification claim.

Missing pricing or policy fields are HOLD context, not automatic BLOCKs, because MCP Registry metadata usually does not contain pricing or commercial policy records.

