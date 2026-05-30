# AOI Test Residual Reconciliation

AOI Agent Discovery 3 had a scoped package PASS, but a full `python -m pytest` run did not finish green because of existing generated registry/datascope payload-state failures outside the staged package.

Discovery 4 classifies that residual state instead of hiding it.

Current classification:

- `HOLD_FULL_SUITE_RESIDUAL_CLASSIFIED`
- generated registry/datascope payload-state residual
- not claimed as package regression
- not safe to stage unrelated generated leftovers
- no full-suite green claim until a full `python -m pytest` passes

The next reconciliation should happen in a narrow package focused on generated registry/datascope payload state.
