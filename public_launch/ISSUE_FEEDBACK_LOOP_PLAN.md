# Issue-Based Feedback Loop

AOI can run a no-contact public beta without private reviewers. Feedback is collected through GitHub Issues instead of direct sales calls, personal outreach, or private reviewer coordination.

## Recommended Labels

- `failed-query`
- `wrong-field`
- `scoring-dispute`
- `missing-source-trace`
- `docs-confusion`
- `install-failure`

## First Golden Queries

1. `Find a cheap image generation API with commercial-use terms.`
2. `Compare MCP servers for browser automation.`
3. `Find AI coding tools with clear pricing and docs.`
4. `Find open-source agent frameworks with active repos.`
5. `Find AI APIs with free tiers and clear rate limits.`

## Response Workflow

1. Issue received.
2. Classify it as failed query, wrong field, scoring dispute, missing source trace, docs confusion, or install failure.
3. Reproduce locally with `python -m ai_objective_index.smoke_all`, the REST API, MCP tools, or the Hugging Face Space.
4. If valid, add the scenario to golden queries or negative controls.
5. Patch scoring, source traces, docs, or data-scope handling.
6. Run claim and no-secrets audits.
7. Release a patch manually if the owner chooses.

## Boundaries

- No direct sales required.
- No private reviewer dependency.
- No automatic posting.
- No claim that `public_beta_mcp` records are verified, security certified, quality guaranteed, or action-ready.
- No payment, booking, login, email, form submission, purchase, contract signing, account connection, supplier claim, or supplier verification.
