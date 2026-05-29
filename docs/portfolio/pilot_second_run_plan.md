# Pilot Second-Run Plan

A `PilotSecondRunPlan` converts accepted or held feedback into a local plan. It can name verticals to rerun, artifacts to reuse, artifacts needed, expected outputs, and status.

Allowed operations are limited to:

- local receipt regeneration planning;
- local redaction checks;
- local claim-boundary checks;
- local feedback memory updates.

Forbidden operations include GitHub API calls, repository cloning, URL fetching, issue or PR comments, merge, deploy, package publishing, live MCP/tool calls, external tool execution, data upload, and model training.

`READY_FOR_LOCAL_SECOND_RUN` means a future local second pass can be prepared. It does not execute the pass and does not authorize external action.
