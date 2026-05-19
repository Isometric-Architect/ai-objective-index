# GitHub Issue Loop Operations

The public beta feedback loop uses GitHub Issues instead of direct outreach.

## Labels

- `public-beta`
- `failed-query`
- `wrong-field`
- `scoring-dispute`
- `missing-source-trace`
- `install-failure`
- `docs-confusion`
- `add-tool`
- `good-first-feedback`

## Handling A Failed Query

1. Reproduce the query locally or in the Hugging Face Space.
2. Capture the data scope, object IDs, score components, missing fields, and source traces.
3. Decide whether the failure belongs in golden queries.
4. Patch source traces, scoring, docs, or data only when the evidence is clear.
5. Run tests and claim/no-secrets audits before pushing.

Issue feedback does not create supplier verification, security certification, quality guarantee, purchasing advice, or action permission.

