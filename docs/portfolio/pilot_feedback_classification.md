# Pilot Feedback Classification

ROE-14 classifies feedback deterministically and locally.

## Classes

- `ACCEPT_AS_FIXTURE_CANDIDATE`: local, redacted, consent-bounded feedback can inform a future fixture, evidence request, or local second pass.
- `HOLD_NEEDS_MORE_CONTEXT`: feedback is too vague to plan a second pass.
- `HOLD_REDACTION_REVIEW`: feedback may include content that needs redaction review.
- `HOLD_OWNER_CONFIRMATION`: consent is unknown or insufficient.
- `HOLD_MANUAL_TRIAGE`: a person must choose the next local path.
- `BLOCK_EXTERNAL_ACTION_REQUEST`: feedback asks for posting, cloning, fetching, merge, deploy, publish, or another forbidden external action.
- `BLOCK_SECRET_OR_PRIVATE_DATA`: feedback includes or declares secret/private-data risk.
- `BLOCK_CERTIFICATION_CLAIM`: feedback asks for certification, proof, readiness, or clearance wording outside the pilot scope.

The classifier does not use external LLMs and does not contact external services.
