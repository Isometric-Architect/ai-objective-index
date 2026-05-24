# QIRA-Code ReleaseGate MVP

QIRA-1 turns QBCPL coding governance into a local/offline release-gate prototype.

It models:

- `BehaviorContract`
- `PatchCandidate`
- `ValidatorPacket`
- `ResidualLedger`
- `PatchReceipt`
- `ActionLicense`
- `QiraReleaseGateReport`

The release gate answers a narrow question: under the current local evidence, what action boundary is appropriate for a patch candidate?

Typical route:

```text
task -> behavior contract -> patch candidate -> validator packet -> residual ledger -> patch receipt -> action license
```

Action boundaries are deliberately conservative. A scoped local pass can allow draft or PR handling, but merge and deploy remain held or blocked unless future, separate evidence packets support them.

QIRA-1 does not execute arbitrary external tools, contact external services, deploy code, request tokens, certify security, guarantee quality, or approve production use.
