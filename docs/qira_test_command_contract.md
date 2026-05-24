# QIRA Test Command Contract

QIRA-3 records project-supplied test commands as a contract. It does not execute them.

The command contract distinguishes:

- recognized local test/static-check command patterns
- dependency installation or container/browser/auth commands that need review
- publish, push, network fetch, destructive shell, or encoded shell commands that must be blocked in the QIRA local MVP
- unrecognized commands that should be held for review

The contract exists so a later GitHub Action or project-owned runner can decide what to execute under its own policy. QIRA-3 itself performs no command execution, no deployment, no network access, no token handling, and no external service call.

Recording a command is not evidence that the command has run. A recorded command is not merge approval, deployment approval, security certification, or quality guarantee.
