# Freshness, Rug-Pull Diff, and Negative Cache Notes

- AOI route decisions are point-in-time artifacts and expire.
- Version changes require recheck.
- Stale metadata routes to `HOLD_STALE_METADATA`.
- Suspicious version or metadata drift routes to `HOLD_RUGPULL_DIFF` or a BLOCK route depending on severity.
- A negative cache stores known bad, deprecated, or untrusted candidates.
- Negative cache entries are not permanent proof; they are recheckable advisory or route artifacts.
- AOI should not expose private anti-gaming details, private probe seeds, private negative controls, provider priors, or commercial routing policy.
- Freshness claims must say when evidence was checked; they must not claim live freshness unless a live check actually occurred.
