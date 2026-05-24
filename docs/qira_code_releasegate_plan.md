# QIRA-Code ReleaseGate Plan

QIRA-Code ReleaseGate is the first implementation vertical because QBCPL already provides a concrete coding contract language.

First MVP:

- CLI command to create a behavior contract from a task packet
- local patch scope validation
- local test command receipt
- residual ledger for missing evidence and behavior gaps
- action-license decision for patch draft, PR open, merge, deploy, and public claim boundaries
- GitHub Action wrapper after the CLI stabilizes

Early product shape:

```text
AI patch or PR -> QBCPL contract -> validators -> residual ledger -> receipt -> release gate decision
```

QIRA can help AI coding workflows reduce unknowns, but it must not claim that a patch is verified, secure, production ready, legally sufficient, or approved for deployment. It returns route and release-gate decisions under stated limits.
