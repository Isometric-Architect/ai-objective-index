# External-Safe Demo Workflow

Workflow:

1. Read ROE-16 local dashboard artifacts.
2. Generate external-safe README, HTML, Markdown, JSON, claim-boundary, known-limits, and operator scripts.
3. Generate manifest and checksums.
4. Run redaction.
5. Run claim audit.
6. Run distribution boundary gate.
7. Optionally dry-run archive creation.
8. Run ROE-17 final gate.

No network, GitHub API, live MCP/tool call, upload, training, deploy, publish, posting, or external repo mutation is part of this workflow.
