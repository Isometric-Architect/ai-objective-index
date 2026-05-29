# ROE-12 Owner-Consented Pilot Intake Kit

ROE-12 adds a local/offline intake kit for future owner-consented pilots across AgentSec Gate, QIRA-Code ReleaseGate, and DataCapsule.

The kit creates intake packets, consent metadata, vertical routes, redaction preflight output, run-plan samples, reviewer instructions, and feedback memory. It does not run a live pilot by itself.

Boundaries:

- No GitHub API calls.
- No repository cloning.
- No URL fetching, crawling, or scraping.
- No live MCP/tool calls.
- No external repo mutation, posting, PR, issue, merge, deploy, upload, model training, or package publish.
- No credential use.
- Not security certification, code correctness proof, legal opinion, privacy audit, license clearance, evaluation-cleanliness proof, quality guarantee, product-readiness claim, or external action authorization.

The intended next step is an owner-consented local pilot dry-run only after a user provides local files or pasted metadata and the redaction preflight passes.
