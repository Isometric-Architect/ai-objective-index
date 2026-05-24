# ROE-0 Portfolio Strategy Summary

Decision: `PASS_PORTFOLIO_SEQUENCE_LOCKED`

ROE-0 keeps AOI as the live public router while preparing a parallel ResidualOps product family. The first move is not to build three broad products at once. The safer sequence is to lock the shared kernel and then ship narrow verticals that reuse the same packet, residual, receipt, and ALLOW/HOLD/BLOCK discipline.

## Implementation Sequence

| Order | Package | Product | Decision |
| --- | --- | --- | --- |
| 0 | ROE-0 | ResidualOps Portfolio Kernel | IMPLEMENT_NOW |
| 1 | QIRA-1 | QIRA-Code ReleaseGate | BUILD_FIRST |
| 2 | AgentSec-1 | AgentSec Gate | BUILD_SECOND |
| 3 | DataCapsule-1 | DataCapsule / AIDREG Engine | BUILD_THIRD |

## Market Priority

| Rank | Product | Reason |
| --- | --- | --- |
| 1 | AgentSec Gate | largest immediate security and MCP/tool-call buyer signal |
| 2 | DataCapsule / AIDREG Engine | large AI data governance platform potential |
| 3 | QIRA-Code ReleaseGate | fastest MVP and proof loop through GitHub/CI workflows |

## Claim Boundary

ROE-0 is strategy, schema, and productization planning. It is not verification, security certification, a quality guarantee, product readiness, legal advice, purchasing advice, or external action authorization.
