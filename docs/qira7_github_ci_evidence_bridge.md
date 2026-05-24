# QIRA-7 GitHub CI Evidence Bridge

QIRA-7 adds an opt-in bridge between a repository's normal CI steps and QIRA-6 evidence intake.

It does not enable an active workflow by default. The reusable composite action lives under `.github/actions/qira-ci-evidence-bridge/`, and the workflow stays in `examples/` until a repository owner intentionally copies or enables it.

## What It Does

```text
normal repository CI step runs tests
-> workflow records check name, command, status, and exit code
-> QIRA-7 writes CI evidence JSON
-> QIRA-6 validates evidence
-> QIRA release gate reruns with augmented packet
```

QIRA-7 does not run project commands on its own. It does not call GitHub APIs, inspect live workflow status, apply patches, merge pull requests, deploy code, upload packages, publish registry metadata, or handle tokens.

## Local Sample

```powershell
python -m ai_objective_index.qira.ci_evidence_bridge --run-sample
python -m ai_objective_index.qira.ci_evidence_bridge --audit-manifest
```

## Reusable Action

The reusable action accepts:

- `packet`
- `output-dir`
- `check-name`
- `check-command`
- `check-status`
- `exit-code`
- `evidence-summary`

The workflow example first runs repository-owned tests, then passes the recorded status into the QIRA bridge. This keeps execution owned by normal CI and keeps QIRA as a local evidence reviewer.

## Boundary

A bridge pass can support scoped QIRA review. It is not security certification, quality guarantee, legal compliance, production readiness, merge approval, deployment approval, or external action authorization.
