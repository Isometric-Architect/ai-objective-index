# Pilot Intake Workflow

The ROE-12 workflow is:

1. Record owner consent.
2. Create a PilotIntakePacket.
3. Run redaction preflight.
4. Route the artifact to AgentSec, QIRA, DataCapsule, or manual triage.
5. Create a local pilot run plan.
6. Package a local/offline pilot receipt only when the route and redaction checks allow it.
7. Store feedback memory for the next pilot.

The workflow stays local. It does not fetch, clone, post, merge, deploy, upload, train, use credentials, or call external APIs.
