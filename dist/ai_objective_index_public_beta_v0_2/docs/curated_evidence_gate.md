# Curated Evidence Gate

The Package 7C evidence gate decides whether a curated object may appear in the `public_beta` data scope.

## PASS

`PASS_PUBLIC_BETA` requires:

- official URL is present and uses `http` or `https`;
- at least one source trace exists;
- object is not a placeholder;
- status is not `VERIFIED` or `ACTION_READY`;
- confidence is at least `0.5`;
- no forbidden action claim is present.

## HOLD

HOLD tokens mean the object is not ready for `public_beta` yet:

- `HOLD_PLACEHOLDER`
- `HOLD_LOW_CONFIDENCE`
- `HOLD_WEAK_SOURCE_TRACE`
- `HOLD_MISSING_TRACE`
- `HOLD_MISSING_OFFICIAL_URL`

## BLOCK

BLOCK tokens mean the row should be fixed before use:

- `BLOCK_INVALID_URL`
- `BLOCK_VERIFIED_WITHOUT_VERIFICATION`
- `BLOCK_MISSING_SOURCE_TRACE`
- `BLOCK_FORBIDDEN_ACTION_CLAIM`

The gate is conservative. Recommendation output is not action permission, and curated data is not supplier verified.
