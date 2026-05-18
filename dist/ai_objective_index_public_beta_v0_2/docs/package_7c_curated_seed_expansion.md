# Package 7C Curated Seed Expansion

Package 7C adds a manual curated data path and evidence gate for real-object candidates. It is Productization Mode work: implementation is allowed, while public/product/security/legal/market claims remain evidence-gated.

## Commands

```powershell
python -m ai_objective_index.curated_index_export
python -m ai_objective_index.curated_eval
python -m ai_objective_index.curated_report_generator
```

## Data Scopes

- `sample`: original sample dataset.
- `generated`: local fixture extraction data.
- `integrated`: sample + generated.
- `curated`: manually curated candidates.
- `public_beta`: curated objects that pass the evidence gate.

Default remains `sample`.

## Intentionally Not Implemented

Package 7C does not crawl, scrape, fetch network data, call external LLM APIs, publish to Hugging Face, post to communities, submit to MCP Registry, verify suppliers, or execute payment, booking, login, email, form, purchase, account connection, or contract workflows.
