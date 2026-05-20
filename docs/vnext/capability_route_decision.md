# Capability Route Decision

Capability route decisions are conservative labels:

- `ALLOW_CANDIDATE`: source-traced candidate routing is allowed inside the claim ceiling.
- `ALLOW_WITH_LIMITS`: candidate can be ranked or compared, but limitations remain.
- `HOLD_EVIDENCE`: evidence is partial or incomplete.
- `HOLD_MISSING_FIELDS`: critical metadata fields are missing.
- `HOLD_POLICY_CLARITY`: policy evidence needs review.
- `HOLD_SECURITY_REVIEW`: security-sensitive context needs review.
- `BLOCK_FORBIDDEN_ACTION`: forbidden real-world action scope appeared.
- `BLOCK_UNSUPPORTED_CLAIM`: unsupported verification, safety, certification, or quality claim appeared.
- `BLOCK_HIGH_RISK_DOMAIN`: high-risk domain boundary blocks routing.
- `BLOCK_NO_SOURCE_TRACE`: no source trace supports the candidate.

ALLOW does not mean verified, safe, best, production-ready, or quality guaranteed.
