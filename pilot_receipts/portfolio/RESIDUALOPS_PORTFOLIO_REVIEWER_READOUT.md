# ResidualOps Unified Pilot Portfolio Readout

ResidualOps is presented here as a local/offline receipt portfolio pattern: Packet -> Check/Probe -> Receipt -> ALLOW/HOLD/BLOCK -> Feedback Memory.

## Verticals

| Vertical | Scope | Gate | ALLOW | HOLD | BLOCK | Primary decision |
| --- | --- | --- | ---: | ---: | ---: | --- |
| AgentSec Gate | local/offline MCP or tool manifest review | `PASS_FIRST_AGENTSEC_PILOT_RECEIPT_READY` | `1` | `1` | `1` | `BLOCK_FORBIDDEN_ACTION` |
| QIRA-Code ReleaseGate | local/offline code-change release-gate review | `PASS_FIRST_QIRA_PILOT_RECEIPT_READY` | `1` | `1` | `1` | `BLOCK_RELEASE_SIDE_EFFECT` |
| DataCapsule / AIDREG Engine | local/offline corpus manifest review | `PASS_FIRST_DATACAPSULE_PILOT_RECEIPT_READY` | `1` | `1` | `1` | `BLOCK_ACTION_USE` |

## Summary Counts

- Verticals: `3`
- ALLOW: `3`
- HOLD: `3`
- BLOCK: `3`

## Matrix

# ResidualOps Vertical Comparison Matrix

| Vertical | Reviewed object | Check type | ALLOW | HOLD | BLOCK | Primary reason | Feedback |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| AgentSec Gate | tool or MCP manifest metadata | metadata permission and forbidden-action review | `1` | `1` | `1` | fixture.local/checkout-action-helper: forbidden action language | `pending` |
| QIRA-Code ReleaseGate | task packet and patch fixture | patch classification, behavior contract, and CI evidence intake | `1` | `1` | `1` | Negative-control fixture includes release/deploy language that a local QIRA pilot cannot authorize. | `pending` |
| DataCapsule / AIDREG Engine | corpus manifest metadata | source-rights, privacy-risk, evaluation-boundary, and use-boundary review | `1` | `1` | `1` | Action use is blocked and declared disallowed uses cannot be upgraded by a manifest-only pilot. | `pending` |

All rows are local/offline receipt artifacts. The matrix is not a security certification, code correctness proof, legal/privacy/license/evaluation proof, quality guarantee, product-readiness claim, or external action authorization.

## Feedback Memory

- Entries indexed: `3`
- Portfolio next actions: owner-consented pilot intake, second-run receipt, unified dashboard, pilot feedback form, private kernel protection.

## What This Is Not

- Not security certification.
- Not code correctness proof.
- Not legal, privacy, license, or evaluation-cleanliness proof.
- Not a quality guarantee.
- Not product readiness.
- No external action authorization.

## Next Actions

- ROE-12 Owner-Consented Pilot Intake Kit.
- Optional AOI 0.3.0a2 MCP Registry recovery backlog.
- Keep private kernels private.
