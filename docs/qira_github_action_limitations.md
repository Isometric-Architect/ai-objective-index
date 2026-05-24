# QIRA GitHub Action Limitations

The QIRA GitHub Action wrapper is dry-run only.

It can:

- read a committed or generated local QIRA task packet;
- run QIRA local metadata review;
- classify patch paths;
- record test-command contracts;
- write JSON and Markdown summaries.

It cannot:

- execute project test commands;
- apply patches;
- push commits;
- create releases;
- deploy code;
- contact external services;
- handle tokens;
- certify security;
- guarantee quality;
- approve production use.

Future packages may add project-owned allowlists or CI execution hooks. Those must stay opt-in and separately gated.
