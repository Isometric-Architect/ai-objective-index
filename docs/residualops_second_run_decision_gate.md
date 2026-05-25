# ResidualOps Second-Run Decision Gate

The second-run gate prevents premature pilot expansion.

## Required Inputs

- ROE-6 feedback memory.
- At least one accepted, non-secret pilot receipt.
- Repository-owner consent for any additional manual run.
- Operator review of the first receipt.

## Gate Behavior

- No accepted receipt: `HOLD_FIRST_PILOT_RECEIPT_REQUIRED`.
- Fail or block signal: `HOLD_FAILURE_REVIEW_REQUIRED`.
- Missing owner consent: `HOLD_OWNER_CONSENT_REQUIRED_FOR_SECOND_RUN`.
- Missing operator review: `HOLD_OPERATOR_REVIEW_REQUIRED`.
- All local conditions met: `PASS_SECOND_RUN_MANUAL_DRY_RUN_READY`.

Even when the gate passes, AOI does not enable workflows or perform external actions. The repository owner still controls any manual run.
