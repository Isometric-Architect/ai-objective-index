# Issue Feedback After Public

AOI uses GitHub Issues as the no-contact public beta feedback loop.

Recommended labels:

- `failed-query`
- `wrong-field`
- `scoring-dispute`
- `missing-source-trace`
- `add-tool`
- `install-failure`
- `docs-confusion`
- `good-first-feedback`
- `public-beta`

Workflow:

1. Receive an issue.
2. Classify it by label.
3. Reproduce locally.
4. Add valid failures to golden queries.
5. Patch scoring, source traces, docs, or data-scope behavior.
6. Run no-secrets and claim audits.
7. Publish a later patch manually if needed.

The issue loop is not direct sales, supplier verification, certification, purchasing advice, or action permission.

## Package 8M Operations

Run the issue-label plan before broad community posting:

```powershell
python -m ai_objective_index.github_issue_labels --dry-run
```

If GitHub CLI is authenticated and label creation is desired:

```powershell
python -m ai_objective_index.github_issue_labels --execute
```

The helper creates or updates labels only. It does not delete labels, post issues, post community announcements, or print tokens.
