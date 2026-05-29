# Pilot Dashboard Workflow

Workflow:

1. Read existing local receipt artifacts.
2. Load ROE-8 through ROE-15 gate results.
3. Build status cards for AgentSec, QIRA, and DataCapsule.
4. Build timeline and aggregate ALLOW/HOLD/BLOCK counts.
5. Generate static JSON, Markdown, and HTML dashboard artifacts.
6. Generate manifest and checksums.
7. Run redaction and claim-boundary checks.
8. Run the ROE-16 dashboard gate.

The workflow is local/offline and does not perform external action.
