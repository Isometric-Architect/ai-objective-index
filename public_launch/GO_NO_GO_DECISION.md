# GO / NO-GO Decision

## Current Private Status

AOI is staged privately on GitHub and Hugging Face.

## Option A: Keep Private

Keep all repositories private and continue internal review.

## Option B: Invite Private Reviewers

Share private links with trusted reviewers only.

## Option C: Switch Public

Only after dry-run checks pass, claim audits pass, and the human owner explicitly confirms.

## Required Checks Before Public

- `python -m pytest`
- `python -m ai_objective_index.public_launch_gate`
- `python -m ai_objective_index.public_visibility_switch --dry-run`
- `python -m ai_objective_index.public_launch_claim_audit`
- `python -m ai_objective_index.no_secrets_audit`
- `python -m ai_objective_index.launch_claim_guard`

## Human Decision

- [ ] Keep private
- [ ] Invite private reviewers
- [ ] Switch public
- [ ] Pause
