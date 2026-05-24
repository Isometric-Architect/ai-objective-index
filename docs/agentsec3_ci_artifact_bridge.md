# AgentSec-3 CI Artifact Bridge

AgentSec-3 adds an opt-in bridge between repository-owned CI and AgentSec-2 policy-gate artifacts.

It does not enable an active workflow by default. The reusable composite action lives under `.github/actions/agentsec-policy-gate-artifact/`, and the workflow stays in `examples/` until a repository owner intentionally copies or enables it.

## What It Does

```text
repository supplies MCP/tool manifests
-> workflow invokes AgentSec bridge
-> AgentSec-2 builds local policy-gate result
-> JSON and Markdown artifacts are written for review
```

AgentSec-3 does not call live MCP servers, execute tools, fetch URLs, and does not call GitHub APIs, post comments, upload packages, publish registry metadata, or handle tokens.

## Local Sample

```powershell
python -m ai_objective_index.agentsec.ci_artifact_bridge --run-sample
python -m ai_objective_index.agentsec.ci_artifact_bridge --audit-manifest
```

## Reusable Action

The reusable action accepts:

- `manifest-set`
- `output-dir`
- `profile`

The manifest set must already exist in the repository checkout. AgentSec reads it as local data and writes review artifacts.

## Boundary

A bridge pass can support scoped metadata review. It is not verification, security certification, quality guarantee, legal compliance, production readiness, registry approval, or external action authorization.
