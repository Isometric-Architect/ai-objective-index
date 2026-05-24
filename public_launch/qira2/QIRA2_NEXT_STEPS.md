# QIRA-2 Next Steps

1. Add a `qira packet` command group with stricter user-facing help.
2. Add patch diff summary and path classification reports.
3. Add optional project-owned test command recording, still without executing arbitrary tools by default.
4. Add a GitHub Action wrapper once packet intake is stable.

QIRA-2 reads local packet files and writes local receipts. It does not execute tests, deploy code, contact external services, request tokens, or certify a patch.
