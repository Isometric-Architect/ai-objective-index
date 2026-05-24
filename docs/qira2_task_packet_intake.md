# QIRA-2 Task Packet Intake

QIRA-2 extends QIRA-1 from a built-in sample report to user-supplied local JSON packets.

The packet contains:

- task
- expected behavior
- changed files or a patch diff
- patch summary
- local evidence summary
- declared claims
- requested action

The packet intake path reads local JSON, derives changed files from metadata or unified diff text, builds a behavior contract and patch candidate, then emits a release-gate report.

QIRA-2 does not apply a patch, execute tests, run external tools, deploy code, contact external services, request tokens, or approve production use. It only records and evaluates user-supplied local evidence.
