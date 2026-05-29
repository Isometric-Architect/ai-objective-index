# Pilot Feedback Memory Update

Feedback memory records how reviewer feedback should influence future local pilots.

Possible update types:

- `add_fixture_candidate`;
- `add_negative_control_candidate`;
- `update_claim_boundary`;
- `request_more_evidence`;
- `update_finding_explanation`;
- `no_change`.

The memory update is a planning artifact. It does not create issues, post comments, mutate repositories, train models, upload data, or authorize any external action.
