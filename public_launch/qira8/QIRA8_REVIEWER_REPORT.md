# QIRA Reviewer Report

Generated: `2026-05-24T07:58:27.040532+00:00`

## Decision

| Field | Value |
| --- | --- |
| QIRA review | `PASS_QIRA6_REVIEW` |
| CI evidence validation | `PASS_CI_EVIDENCE_ACCEPTED` |
| Release gate | `PASS_CONTRACT_SCOPED` |
| Bridge decision | `PASS_QIRA7_CI_EVIDENCE_BRIDGE` |
| Commands executed by QIRA | `False` |
| GitHub API used by QIRA | `False` |
| PR comment posted | `False` |

## Action License

| Action | Decision |
| --- | --- |
| Patch draft | `ALLOW` |
| PR open | `ALLOW` |
| Merge | `HOLD` |
| Deploy | `BLOCK` |
| Public claim | `ALLOW_SCOPED_INTERNAL` |

Decision reason: Scoped local contract evidence supports draft/PR handling, while merge and deploy remain separately gated.

## Evidence Summary

| Field | Value |
| --- | --- |
| Tests passed in supplied evidence | `True` |
| Accepted commands | `1` |
| Changed files | `3` |
| Path categories | `{'docs': 1, 'source': 1, 'test': 1}` |
| Command contract | `PASS_TEST_COMMAND_CONTRACT` |
| Commands recorded | `2` |

## Holds Or Blocks

- No validation block or hold reasons recorded.

## Reviewer Notes

- Scoped QIRA pass can support patch draft or PR review under recorded evidence.
- Merge, deploy, package upload, registry submission, and production use remain separately gated.
- This report is generated from local artifacts and does not post to GitHub.

## Must Not Claim

- do not claim verified status
- do not claim safety
- do not claim security certification
- do not claim quality guarantee
- do not claim production readiness
- do not claim legal compliance
- do not claim deployment approval
- do not claim external action authorization
