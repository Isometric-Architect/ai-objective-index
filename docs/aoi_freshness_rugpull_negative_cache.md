# AOI Freshness, Rug-Pull Diff, and Negative Cache

AOI route decisions are point-in-time receipts. They expire.

Freshness hardening should track:

- `last_checked_at`
- source trace age
- registry payload version
- stale warnings
- recheck policy

Suspicious metadata drift should route to `HOLD_RUGPULL_DIFF` or a BLOCK route depending on severity. Known bad, deprecated, or untrusted candidates can enter a negative cache, but that cache is not permanent proof. It is a recheckable advisory and route artifact.

The implementation must not disclose private anti-gaming details, private negative controls, probe seeds, provider priors, or commercial routing policy.
