# QIRA GitHub CI Bridge Limitations

The QIRA-7 bridge is deliberately narrow.

Allowed:

- receive a local QIRA task packet path;
- receive a recorded CI check name, command string, status, and exit code;
- write QIRA CI evidence JSON;
- run QIRA's local evidence validation and review code.

Not allowed:

- fetching pull requests;
- calling GitHub APIs;
- reading workflow logs from GitHub;
- executing arbitrary project commands;
- applying patches;
- opening, merging, or closing pull requests;
- deploying code;
- uploading packages;
- publishing registry metadata;
- reading or printing secrets.

The example workflow is not active. It is a copy-and-enable template for a repository owner. QIRA remains an evidence and release-gate layer, not a CI orchestrator, security certification system, quality guarantee, or production authorization service.
