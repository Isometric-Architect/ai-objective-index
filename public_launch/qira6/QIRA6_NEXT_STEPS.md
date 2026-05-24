# QIRA-6 Next Steps

1. Let repository CI produce a QIRA CI evidence JSON artifact after tests/static checks run.
2. Feed that artifact into QIRA-6 together with the QIRA task packet.
3. Keep QIRA as an evidence reviewer, not a command executor.
4. Add an opt-in workflow that uploads packet and evidence artifacts only when the repository owner enables it.

QIRA-6 does not run tests, call GitHub APIs, inspect live CI, apply patches, merge, deploy, upload, publish, handle tokens, certify security, guarantee quality, or authorize production actions.
