# AOI Route Semantics Hardening

External feedback converged on one point: ALLOW/HOLD/BLOCK is too coarse for ordinary AI agents.

AOI should add granular route classes such as `FOUND_ONLY`, `ALLOW_DISCOVERY_ONLY`, `ALLOW_READ_ONLY`, `ALLOW_DRAFT_ONLY`, `HOLD_STALE_METADATA`, `HOLD_RUGPULL_DIFF`, `BLOCK_DESTRUCTIVE_ACTION`, and escalation routes for AgentSec, QIRA, DataCapsule, and human approval.

Required separation:

- FOUND != TRUSTED
- TRUSTED != AUTHORIZED
- AUTHORIZED != EXECUTABLE
- route decision != security certification
- route decision != action authorization

This hardening keeps AOI useful first while preventing ordinary agents from treating search results or metadata as permission to act.
