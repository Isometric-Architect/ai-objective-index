# Feedback Second-Run Skipped Candidates

Skipped-candidate reports preserve why a feedback candidate did not execute.

Common reasons:

- `HOLD_NEEDS_ARTIFACT`: a local redacted artifact or evidence summary is missing.
- `HOLD_CONSENT_UNCLEAR`: consent is not clear enough for a local second run.
- `HOLD_CONTEXT_REQUIRED`: the reply needs manual triage.
- `BLOCK_EXTERNAL_ACTION`: the candidate asks for external mutation, posting, or live execution.
- `BLOCK_SECRET`: sensitive content was detected.
- `BLOCK_OVERCLAIM`: the request asks for a certification, proof, readiness, or action-authorization claim.

Skipped candidates can be retried only after the missing local/redacted artifact or context is provided.
