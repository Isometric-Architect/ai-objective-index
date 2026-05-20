# Objective Router Response Standard

`ObjectiveRouteResponse` contains:

- `schema`: `AOI_ObjectiveRouteResponse/v0.1`
- `query`
- `objective`
- `domain`
- `data_scope`
- `generated_at`
- `route_summary`
- `results`
- `known_limits`
- `must_not_claim`
- `next_actions`
- execution flags

`route_summary` contains:

- total candidates
- allow count
- hold count
- block count
- top decision reasons
- claim ceiling

`must_not_claim` includes verified, safe, security certified, quality guaranteed, production ready, legal/financial/medical advice, and purchasing advice.

The router must never upgrade a HOLD or BLOCK into ALLOW without stronger evidence. Constraints can make a route stricter, not looser.
