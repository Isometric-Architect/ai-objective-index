# Public Data Intake Policy

Package 7D permits a narrow public-data intake path for AOI.

Allowed:

- Official MCP Registry API metadata only.
- Read-only HTTP GET only when `--allow-network` is explicitly passed.
- Controlled live run endpoint: `GET /v0.1/servers?limit=50`.
- Local fixture mode.
- Manual download fallback.
- Local cache under `data/registry/`.

Not allowed:

- broad live crawling;
- arbitrary website scraping;
- HTML parsing;
- link following;
- login, paywall, private, or token-gated data;
- Product Hunt, G2, random directories, or general web pages;
- external LLM extraction;
- supplier claim/verify;
- payment, booking, login, email sending, form submission, purchase, account connection, or contract signing.

Registry metadata is mapped to `EXTRACTED_UNVERIFIED` AOI objects. It is not a security certification, quality guarantee, supplier verification, or action license.

Default max server count is `50`.

Package 7F candidate calibration uses saved registry metadata only. It does not run live network. A `public_beta_mcp` candidate is a registry metadata candidate, not a verified object, security certification, quality guarantee, purchasing recommendation, or action permission.

Package 7G requires anti-fixture protection: fixture exports must not silently overwrite a real/manual `mcp_registry_raw_v0_1.json`. Real/manual raw may be activated from `data/registry/` or from a repository-root `mcp_registry_raw_v0_1.json`, then reprocessed offline.

Package 8A uses the activated local raw payload to prepare public-beta-facing assets. It does not perform additional live network access, crawling, scraping, link following, repository fetches, package fetches, publishing, or registry submission.
