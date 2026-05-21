# ProbeCard

`ProbeCard` describes one local metadata check for a candidate capability.

Key fields:

- `probe_type`: source trace, missing field, policy clarity, docs, repository, license, unsupported claim, forbidden action, negative control, or local fixture.
- `capability_id` and optional `object_id`: the local AOI object to inspect.
- `sandbox_policy`: must remain no network, no external tool execution, no subprocess, local data only.
- `forbidden_claims` and `forbidden_actions`: wording and actions that trigger conservative blocks.
- `claim_ceiling`: states that the probe is not verification or action authorization.
