# AI Objective Index Public Beta v0.2

AI Objective Index (AOI) is a read-only MCP/API benchmark and objective comparison engine for AI tools, APIs, SaaS products, and MCP servers.

## Current Public Beta Data Source

The public beta MCP data source is Official MCP Registry metadata obtained as raw JSON and processed locally.

- Raw payload mode: `manual_raw`
- MCP registry objects: `50`
- Source traces: `191`
- `public_beta_mcp` candidates: `50`
- Fixture leak detected: `false`

## Run Locally

```powershell
python -m ai_objective_index.api
python -m ai_objective_index.mcp_smoke
python hf_demo/app.py
python -m ai_objective_index.datascope_qa
```

## Data Scopes

- `sample`: original sample records
- `generated`: local fixture extraction records
- `integrated`: sample + generated records
- `curated`: manually curated candidates
- `public_beta`: curated public beta candidates
- `mcp_registry`: all local Official MCP Registry metadata records
- `public_beta_mcp`: registry metadata candidates, not verified

## Boundary

AOI is read-only. `public_beta_mcp` candidates are not verified MCP servers, not security certified, not quality guaranteed, not purchasing advice, and not action-ready.

AOI does not buy, book, pay, log in, send email, submit forms, purchase, connect accounts, verify suppliers, or sign contracts. Publishing to GitHub, Hugging Face, MCP Registry, or communities is manual and not performed by this packager.

## Private Deployment Links

- GitHub private staging repo: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space, private: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset, private: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample
- MCP Registry submission: HOLD, manual only.

These links are private deployment links unless the owner manually changes visibility. They are not a public release claim. `public_beta_mcp` records are source-traced registry metadata candidates; they are not verified, not safe/certified, not security certified, not a quality guarantee, and not purchasing advice.
