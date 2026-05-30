# AOI Final Argument Preflight

Final argument preflight checks the concrete arguments an agent wants to pass into a capability.

The reason is simple: a capability may be acceptable for discovery or read-only review, while one proposed argument set makes the call risky.

Examples:

- `filesystem.write` with overwrite intent routes to HOLD or BLOCK.
- `github.create_pr` with release intent escalates to QIRA.
- `email.send` to an external recipient escalates to human approval.
- `database.query` containing update/delete/drop intent routes to HOLD or BLOCK.
- `browser.submit_form` escalates to human approval.
- token-like input blocks as secret/private data.

Final argument preflight does not authorize external action. It is a pre-use route receipt for the proposed call shape.
