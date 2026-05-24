# QBCPL Coding Governance

QBCPL is the coding governance layer for the first ROE implementation vertical. It turns a user task into a behavior contract, patch candidate, validator packet, residual ledger, receipt, and action license.

The working route is:

```text
Q -> BehaviorContract -> PatchCandidate -> ValidatorPacket -> ResidualLedger -> PatchReceipt -> ActionLicense -> ALLOW/HOLD/BLOCK
```

The important non-inflation rule is simple: a local test pass does not automatically mean merge, deploy, security readiness, legal readiness, product readiness, or public claim readiness.

QIRA-Code ReleaseGate should begin with local and CI-friendly checks:

- task contract extraction
- patch path and scope validation
- test command scope validation
- residual ledger generation
- patch receipt generation
- action-license decision for draft, PR, merge, deploy, and public claim boundaries

The first MVP should be local/offline by default. It should not execute arbitrary external tools, contact external services, request tokens, or authorize production deployment.
