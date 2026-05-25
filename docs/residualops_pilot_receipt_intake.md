# ResidualOps Pilot Receipt Intake

The pilot receipt intake gate accepts manually recorded results from an owner-consented pilot run.

## Required Shape

The receipt should include:

- vertical id: `agentsec`, `qira`, or `datacapsule`
- repository alias, not private customer identifiers
- workflow artifact name
- owner consent flag
- outcome: `allow`, `hold`, `block`, `partial`, or `fail`
- hold reasons, block reasons, missing inputs, and feedback notes

## Safety Rules

- Do not include tokens, secrets, `.env` contents, account details, private customer data, or partner strategy.
- Do not include private ranking calibration values, threshold policy, provider priors, private negative controls, private probe seeds, or commercial routing policy.
- Do not claim verification, security certification, quality guarantee, product readiness, legal/privacy/license/evaluation proof, purchasing advice, or action authorization.

Receipts that contain token-like strings or unsupported public claims are blocked.
