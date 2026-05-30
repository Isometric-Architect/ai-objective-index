# Feedback Second-Run Bridge Workflow

1. Read local ROE-19 feedback reply second-run candidates.
2. Select only `READY_FOR_LOCAL_SECOND_RUN` candidates.
3. Skip HOLD/BLOCK candidates and write skipped-candidate reports.
4. Execute local receipt update logic for selected candidates.
5. Generate bridge trace, receipt, memory update, readout, and redaction report.
6. Run the ROE-20 gate.

The workflow keeps all work local and redacted. Feedback never authorizes external action.
