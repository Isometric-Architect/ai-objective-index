# Pilot Feedback Workflow

ROE-14 uses this local/offline workflow:

1. Reviewer fills the feedback form.
2. Feedback is converted into a `PilotFeedbackPacket`.
3. Redaction preflight checks token-like strings, secrets, personal data, raw private rows, and private kernel disclosures.
4. The deterministic classifier assigns an ACCEPT, HOLD, or BLOCK class.
5. A second-run plan is generated without executing it.
6. A feedback memory update records the next local action.
7. The ROE-14 gate checks claim boundaries and confirms no external action is authorized.

The workflow is intentionally conservative. Unknown consent, unclear context, redaction concerns, external action requests, private data, and certification/proof requests stay on HOLD or BLOCK.
