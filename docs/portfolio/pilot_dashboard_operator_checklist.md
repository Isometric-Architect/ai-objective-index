# Pilot Dashboard Operator Checklist

1. Generate the dashboard:

```powershell
python -m ai_objective_index.portfolio.pilot_dashboard_builder
```

2. Run the dashboard gate:

```powershell
python -m ai_objective_index.portfolio.roe16_dashboard_gate
```

3. Inspect the static HTML locally.

4. Confirm the claim banner is visible.

5. Confirm all prior gates are represented.

6. Do not add external scripts, forms, API calls, raw private data, tokens, deploy steps, posting steps, certification claims, product-readiness claims, or action-authorization claims.
