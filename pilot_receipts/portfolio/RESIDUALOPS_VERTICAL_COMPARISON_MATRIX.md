# ResidualOps Vertical Comparison Matrix

| Vertical | Reviewed object | Check type | ALLOW | HOLD | BLOCK | Primary reason | Feedback |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| AgentSec Gate | tool or MCP manifest metadata | metadata permission and forbidden-action review | `1` | `1` | `1` | fixture.local/checkout-action-helper: forbidden action language | `pending` |
| QIRA-Code ReleaseGate | task packet and patch fixture | patch classification, behavior contract, and CI evidence intake | `1` | `1` | `1` | Negative-control fixture includes release/deploy language that a local QIRA pilot cannot authorize. | `pending` |
| DataCapsule / AIDREG Engine | corpus manifest metadata | source-rights, privacy-risk, evaluation-boundary, and use-boundary review | `1` | `1` | `1` | Action use is blocked and declared disallowed uses cannot be upgraded by a manifest-only pilot. | `pending` |

All rows are local/offline receipt artifacts. The matrix is not a security certification, code correctness proof, legal/privacy/license/evaluation proof, quality guarantee, product-readiness claim, or external action authorization.
