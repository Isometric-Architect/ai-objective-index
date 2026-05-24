# QIRA CI Evidence Limitations

QIRA-6 is an evidence intake layer, not a CI runner.

Allowed inputs:

- local QIRA task packet JSON;
- local CI evidence JSON;
- recorded test/static-check command strings;
- recorded CI status summaries.

Out of scope:

- running tests or shell commands;
- fetching GitHub workflow status;
- calling GitHub APIs;
- reading secrets;
- applying patches;
- merging pull requests;
- deploying code;
- uploading packages;
- publishing registry metadata.

## Conservative Decisions

If evidence is missing, QIRA returns `HOLD_CI_EVIDENCE_MISSING`.

If checks are skipped, unknown, or commands need review, QIRA returns `HOLD_CI_EVIDENCE_PARTIAL`.

If checks fail, commands are unsafe, unsupported claims are present, or token-like strings appear, QIRA blocks the evidence.

If evidence passes, QIRA can support a scoped local release-gate pass. It still must not be described as security certification, quality guarantee, legal compliance, production readiness, merge approval, deployment approval, or action authorization.
