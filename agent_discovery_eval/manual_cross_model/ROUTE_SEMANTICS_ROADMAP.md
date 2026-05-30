# Route Semantics Roadmap

AOI route labels need to become more granular than ALLOW/HOLD/BLOCK so ordinary agents can move fast without confusing discovery with execution readiness.

## Route Classes

- `FOUND_ONLY`
- `SCHEMA_READABLE`
- `ALLOW_DISCOVERY_ONLY`
- `ALLOW_READ_ONLY`
- `ALLOW_DRAFT_ONLY`
- `ALLOW_LOW_RISK_CALL`
- `HOLD_MISSING_FIELDS`
- `HOLD_AUTHORIZATION`
- `HOLD_SECURITY_REVIEW`
- `HOLD_PRIVACY_REVIEW`
- `HOLD_POLICY_CLARITY`
- `HOLD_STALE_METADATA`
- `HOLD_RUGPULL_DIFF`
- `BLOCK_UNTRUSTED_SOURCE`
- `BLOCK_DESTRUCTIVE_ACTION`
- `BLOCK_SECRET_OR_PRIVATE_DATA`
- `BLOCK_CERTIFICATION_CLAIM`
- `ESCALATE_AGENTSEC`
- `ESCALATE_QIRA`
- `ESCALATE_DATACAPSULE`
- `ESCALATE_HUMAN_APPROVAL`

## Required Separations

- FOUND != TRUSTED
- TRUSTED != AUTHORIZED
- AUTHORIZED != EXECUTABLE
- route decision != security certification
- route decision != action authorization

## Design Notes

- `FOUND_ONLY` means AOI found a candidate, not that the candidate is trusted.
- `ALLOW_DISCOVERY_ONLY` is appropriate when an agent may summarize or compare candidates but must not call the tool.
- `ALLOW_READ_ONLY` is for low-risk inspection when source traces and permission boundaries are adequate.
- `ALLOW_DRAFT_ONLY` lets an agent prepare a plan, diff, or message without sending or mutating anything.
- `ALLOW_LOW_RISK_CALL` is reserved for narrow, idempotent, bounded calls with permission and data boundaries known.
- HOLD routes must include a next action and should be exception paths for low-risk read-only cases.
- BLOCK routes prevent the proposed action; they do not prove the candidate is globally unusable.
- ESCALATE routes send evidence to AgentSec, QIRA, DataCapsule, or human approval without authorizing external action.

This roadmap is a design draft. It is not a security certification, product readiness statement, or action authorization.
