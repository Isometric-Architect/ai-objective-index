# ResidualOps Owner Consent Gate

ROE-5 separates onboarding preparation from workflow enablement.

The public repo can include instructions, examples, checklists, and dry-run plans. It must not enable a workflow in a target repository without repository owner consent.

## Consent Required Before

- copying any workflow into `.github/workflows/` of a target repository
- running GitHub API automation
- posting PR comments
- enabling automatic triggers
- processing private repository data

## Public-Safe Consent Status

The committed ROE-5 consent gate intentionally remains `HOLD_OWNER_CONSENT_REQUIRED_BEFORE_ENABLEMENT`.

That HOLD is expected. It means the kit is ready, but a real pilot still needs owner consent outside this public artifact.

Do not commit consent records containing private account data, tokens, partner-specific strategy, or private repository information.
