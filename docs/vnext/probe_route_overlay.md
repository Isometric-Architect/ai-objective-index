# Probe Route Overlay

`ProbeRouteOverlay` applies local probe results to an Objective Router response.

Allowed effects:

- `NO_CHANGE`
- `ADD_WARNING`
- `DOWNGRADE_TO_HOLD`
- `DOWNGRADE_TO_BLOCK`
- `DO_NOT_UPGRADE`

Probe overlays can make a route more conservative. They cannot turn a HOLD into an ALLOW and cannot create verified, certified, guaranteed, or action-authorized status.
