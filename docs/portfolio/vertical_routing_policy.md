# Vertical Routing Policy

ROE-12 routes artifacts by local metadata type:

| Artifact type | Route |
| --- | --- |
| `mcp_manifest`, `tool_manifest` | AgentSec Gate |
| `pr_diff`, `patch_text`, `ci_summary` | QIRA-Code ReleaseGate |
| `dataset_manifest`, `corpus_manifest`, `dataset_card` | DataCapsule |
| `mixed` | HOLD manual triage |
| `unknown` | HOLD manual triage |

Unknown consent blocks or holds the route. Requested external action blocks the route. Raw private data should be replaced with a redacted manifest or summary before a pilot run plan proceeds.
