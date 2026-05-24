# QIRA Reviewer Report Limitations

The QIRA reviewer report is a local summary of QIRA artifacts. It is not a PR comment poster, CI runner, merge gate, deployment system, security certification, quality guarantee, legal compliance result, or production readiness decision.

It can summarize:

- QIRA review decision;
- CI evidence validation decision;
- action-license decisions;
- changed-file and command metadata;
- hold or block reasons;
- artifact hashes.

It cannot:

- prove the code is correct;
- prove security;
- guarantee quality;
- authorize merge or deployment;
- publish packages;
- submit registries;
- contact external services;
- handle credentials.

Generated PR comment drafts are drafts only. They should be posted only by a future explicit repository-owner opt-in flow.
