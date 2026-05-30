# External Share Refresh Workflow

1. Load ROE-21 dashboard refresh artifacts.
2. Build the V2 static share pack in `external_share_pack_v2/`.
3. Generate the stale-to-refreshed delta.
4. Generate manifest and checksums.
5. Run redaction.
6. Run claim audit.
7. Run distribution boundary gate.
8. Optionally run archive dry-run.
9. Run the ROE-22 external share refresh gate.

The workflow must keep skipped candidates visible. QIRA, DataCapsule, and Portfolio skipped candidates are HOLD, not success.
