# Pilot Dry-Run Workflow

The dry-run workflow is:

1. Load ROE-12 sample intake packets.
2. Confirm redaction and route boundaries.
3. Route each packet to a vertical.
4. Call the selected local/offline pilot packager.
5. Collect each vertical receipt result.
6. Aggregate ALLOW/HOLD/BLOCK counts.
7. Write reviewer readout and feedback memory.
8. Run the dry-run gate.

The workflow stays local and uses direct Python function imports only.
