# Freshness, Rug-Pull, and Negative Cache Spec

AOI route decisions are point-in-time artifacts. Version changes require recheck. Stale metadata routes to `HOLD_STALE_METADATA`. Suspicious version drift routes to `HOLD_RUGPULL_DIFF`. Negative cache hits are recheckable route artifacts, not permanent proof.

No private anti-gaming rules, probe seeds, negative controls, provider priors, or commercial routing policy are disclosed.
