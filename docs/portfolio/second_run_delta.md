# Second-Run Delta

The second-run delta compares a prior local receipt to a new local second-run result.

The delta records:

- changed findings;
- unchanged findings;
- added fixture candidates;
- added negative-control candidates;
- explanation updates;
- next-action updates;
- claim-boundary changes;
- decision-change counts.

Safety rules are explicit:

- no unsafe BLOCK-to-ALLOW upgrade;
- no HOLD-to-ALLOW upgrade without local evidence;
- no certification upgrade;
- no external action authorization.

ROE-15 sample deltas keep the original ALLOW/HOLD/BLOCK counts unchanged and focus on clearer explanations and follow-up actions.
