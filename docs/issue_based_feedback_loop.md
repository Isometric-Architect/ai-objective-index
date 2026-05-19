# Issue-Based Feedback Loop

AOI can use GitHub Issues as the public beta feedback loop when private reviewers are unavailable.

## Labels

- `failed-query`
- `wrong-field`
- `scoring-dispute`
- `missing-source-trace`
- `docs-confusion`
- `install-failure`

## Workflow

1. Issue received.
2. Classify by label.
3. Reproduce locally with the API, MCP helpers, Hugging Face Space, or `python -m ai_objective_index.smoke_all`.
4. If valid, add the case to golden queries or negative controls.
5. Patch scoring, source traces, docs, data scope behavior, or claim language.
6. Re-run tests and launch guards.
7. Release a patch manually if desired.

## Boundary

Issue feedback is evidence for improvement, not proof that AOI is verified, safe, security certified, quality guaranteed, production-ready, or suitable for purchasing decisions.
