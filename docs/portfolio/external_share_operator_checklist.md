# External Share Operator Checklist

1. Generate the pack:

```powershell
python -m ai_objective_index.portfolio.external_share_pack_builder
```

2. Run the final gate:

```powershell
python -m ai_objective_index.portfolio.roe17_external_share_gate
```

3. Open `external_share_pack/RESIDUALOPS_EXTERNAL_SAFE_DEMO.html` locally.

4. Confirm the claim ceiling banner is visible before any walkthrough.

5. Do not add scripts, links, forms, live connectors, credentials, raw private data, tokens, private kernels, deployment steps, posting steps, certification claims, product-readiness claims, or action-authorization claims.
