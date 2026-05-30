# Feedback Second-Run Candidate Selection

Selection rules:

- `READY_FOR_LOCAL_SECOND_RUN` can be selected only when the candidate is local/redacted and does not request external action.
- `HOLD_NEEDS_ARTIFACT` is skipped until the local redacted artifact is supplied.
- `HOLD_CONSENT_UNCLEAR` is skipped until consent is clarified.
- `BLOCK_*` candidates are skipped and reported as blocked.
- Candidates requesting issue creation, comments, merge, deploy, package publish, live MCP/tool use, upload, training, or API calls cannot execute.

Selection does not change ALLOW/HOLD/BLOCK findings by itself.
