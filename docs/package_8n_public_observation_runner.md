# Package 8N: Public Observation Runner

Package 8N starts the 72-hour public observation workflow and reviews residual working-tree changes after public launch operations.

Run:

```powershell
python -m ai_objective_index.public_metrics_snapshot
python -m ai_objective_index.public_observation_runner --phase 0h
python -m ai_objective_index.residual_worktree_review
python -m ai_objective_index.observation_decision_gate --phase 0h
```

Optional later phases:

```powershell
python -m ai_objective_index.public_observation_runner --phase 24h
python -m ai_objective_index.public_observation_runner --phase 48h
python -m ai_objective_index.public_observation_runner --phase 72h
```

Package 8N does not post to communities, create a GitHub Release, submit to MCP Registry, delete leftover files, stage all changes, force push, print/store tokens, crawl, scrape, follow links, call external LLM APIs, or execute real-world actions.

The default next decision remains `observe_72h` unless public URL checks, claim audits, or residual worktree review identify a concrete issue.
