# DataCapsule Pilot Receipt Workflow

The ROE-10 workflow is intentionally local:

1. Read a local corpus manifest or sample fixture.
2. Summarize source and rights metadata.
3. Summarize privacy and PII risk from declared fields.
4. Summarize evaluation-overlap and split-policy fields.
5. Build a use boundary.
6. Create a DataCapsule pilot receipt.
7. Write a reviewer readout.
8. Store feedback memory for future manifest schema, fixture, and negative-control updates.

The workflow records evidence and limits. It does not inspect raw corpus content, prove legal/privacy/license status, prove evaluation cleanliness, authorize training, or authorize actions.
