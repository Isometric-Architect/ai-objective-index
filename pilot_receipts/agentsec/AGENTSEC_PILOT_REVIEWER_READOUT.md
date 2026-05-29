# AgentSec Pilot Reviewer Readout

Pilot: `agentsec-pilot-9211d03b8e0b`

Project: `AgentSec sample pilot`

## Scope

- Manifest-only review: `True`
- Live MCP call: `False`
- Live tool execution: `False`
- GitHub API call: `False`
- External network: `False`

## Summary

| Field | Value |
| --- | --- |
| Manifests | `3` |
| Tools | `3` |
| Permissions | `2` |
| ALLOW | `1` |
| HOLD | `1` |
| BLOCK | `1` |

## Findings

| Finding | Decision | Category | Severity | Next Action |
| --- | --- | --- | --- | --- |
| `agentsec-pilot-finding-1` | `ALLOW` | `unknown` | `info` | keep as metadata-only candidate |
| `agentsec-pilot-finding-2` | `HOLD` | `permission_scope` | `medium` | review metadata before use |
| `agentsec-pilot-finding-3` | `BLOCK` | `forbidden_action` | `high` | remove or justify blocked manifest language |

## Known Limits

- This is a local/offline manifest review artifact.
- It is not security certification.
- It is not a compliance audit.
- It is not a quality guarantee.
- It is not a live exploit scan.
- It is not production-readiness proof.
- It does not authorize external actions.
