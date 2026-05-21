# Receipt Route Overlay

`ReceiptRouteOverlay` applies local receipt memory to an Objective Router response.

Overlay effects:

- `NO_CHANGE`
- `ADD_WARNING`
- `DOWNGRADE_TO_HOLD`
- `DOWNGRADE_TO_BLOCK`
- `DO_NOT_UPGRADE`

The overlay is intentionally conservative. Failure receipts can add warning or downgrade a candidate. Success receipts cannot upgrade a HOLD route into ALLOW in this MVP.

Final claim ceiling:

Receipt route overlay is route context with local memory. It is not verified, not security certified, not a quality guarantee, and no action authorization is granted.

