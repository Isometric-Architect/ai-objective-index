# Package 8M: Public Ops Baseline

Package 8M creates the first public operations baseline after visibility is public.

It does not post to communities, create a GitHub Release, submit to MCP Registry, crawl, scrape, follow links, call external LLM APIs, print/store tokens, force push, or execute real-world actions.

## Commands

```powershell
python -m ai_objective_index.public_ops_baseline
python -m ai_objective_index.worktree_hygiene_audit
python -m ai_objective_index.github_issue_labels --dry-run
python -m ai_objective_index.github_issue_labels --execute
python -m ai_objective_index.observation_log
python -m ai_objective_index.release_next_decision_gate
```

`github_issue_labels --execute` requires local GitHub CLI authentication. It creates or updates labels only; it does not delete labels or post issues.

## Default Mode

The default recommendation is `observe_72h`. Public visibility is live, but the next operational step should be measured observation unless the owner explicitly chooses a release, community post, MCP Registry submission, or data expansion package.

