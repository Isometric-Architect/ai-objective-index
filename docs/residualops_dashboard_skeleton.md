# ResidualOps Dashboard Skeleton

The ROE-2 dashboard is a local Markdown and JSON status view over the shared artifact manifest.

It shows:

- current vertical package
- primary decision
- coarse status bucket
- artifact count
- conservative portfolio note

The dashboard deliberately avoids private kernel internals. It does not expose exact weights, thresholds, provider priors, anti-gaming rules, private negative controls, private probe seeds, commercial routing policy, or private data strategy.

Run:

```powershell
python -m ai_objective_index.residualops_dashboard
python -m ai_objective_index.residualops_dashboard_audit
```
