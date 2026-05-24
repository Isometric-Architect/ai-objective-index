# QIRA-4 Next Steps

1. Add a real repository fixture packet generated from a pull request diff.
2. Add project-owned allowlist support before any command execution is considered.
3. Keep the default GitHub Action wrapper in dry-run mode.
4. Add active workflow only when the repository owner intentionally enables it.

QIRA-4 provides a reusable action wrapper. It does not auto-enable a workflow, execute project commands, deploy code, or handle tokens.
