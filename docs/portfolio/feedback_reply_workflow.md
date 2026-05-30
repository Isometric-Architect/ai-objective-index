# Feedback Reply Workflow

Workflow:

1. Save a reply as a local text or Markdown file, or use the sample fixtures.
2. Run local redaction.
3. Build a feedback reply packet.
4. Classify the reply.
5. Route it to AgentSec, QIRA, DataCapsule, Portfolio, manual triage, or block.
6. Generate a triage entry.
7. Generate feedback memory and second-run candidates only when local, redacted, and claim-bounded.

The workflow never sends, posts, fetches, uploads, deploys, or calls external APIs.
