# ROE-2 Shared Artifact Manifest

ROE-2 creates a local manifest that indexes the current public artifacts for:

- QIRA-Code ReleaseGate
- AgentSec Gate
- DataCapsule / AIDREG Engine

The manifest records artifact paths, file sizes, SHA-256 hashes, primary decisions, decision buckets, known limits, and conservative safety flags. It is a read-only operations index over existing local files.

Run:

```powershell
python -m ai_objective_index.residualops_artifact_manifest
```

The manifest does not execute tools, enable workflows, fetch URLs, call GitHub APIs, upload packages, submit MCP Registry metadata, certify security, guarantee quality, prove product readiness, or authorize actions.
