# Feedback Reply Packet

The feedback reply packet records the redacted reply text, reviewer type, related vertical, consent signal, requested action, and safety flags.

Important flags include:

- `external_action_requested`
- `certification_or_readiness_claim_requested`
- `token_or_secret_detected`
- `private_kernel_detected`

These flags are used to block unsafe follow-up paths before a route or second-run candidate can be created.
