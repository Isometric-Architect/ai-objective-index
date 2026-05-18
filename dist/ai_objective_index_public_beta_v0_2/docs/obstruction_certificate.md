# Obstruction Certificate

An obstruction certificate is a productive non-closure. It records why AOI cannot safely promote a field or output beyond the current source-governed claim ceiling.

Tokens:

- `HOLD_SOURCE`
- `HOLD_POLICY`
- `HOLD_PRICE`
- `HOLD_FRESHNESS`
- `HOLD_VALIDATOR`
- `HOLD_USE_RIGHT`
- `HOLD_ACTION_BOUNDARY`
- `BLOCK_UNSAFE_CLAIM`
- `BLOCK_FORBIDDEN_ACTION`
- `BLOCK_FORBIDDEN_PROMOTION`

Each certificate includes:

- object id;
- token;
- reason;
- missing evidence;
- next action;
- severity;
- source trace ids.

HOLD is not failure. HOLD means the output should remain bounded until the missing evidence or validator step is supplied.
