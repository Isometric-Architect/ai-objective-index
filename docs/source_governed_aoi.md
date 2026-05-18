# Source-Governed AOI

Package 6D-S upgrades AOI from read-only objective ranking into a source-governed objective decision engine.

The upgrade follows these rules:

- source status before evidence;
- validator before claim;
- packet before output;
- use-right separation;
- recommendation is not action license;
- HOLD/BLOCK boundaries stay visible;
- source traces and claim ceilings are checked before promotion.

Generated and sample records may be searched, scored, compared, explained, and reported, but they cannot be silently promoted to verified supplier claims.

AOI remains read-only and local-data-only in this package. It does not crawl live sites, fetch network data, call external LLM APIs, publish, post, buy, book, pay, log in, email, submit forms, connect accounts, purchase, or sign contracts.
