# GitHub Release Draft: AI Objective Index Public Beta v0.2

AI Objective Index is a read-only MCP/API benchmark and objective comparison engine for AI tools, APIs, SaaS products, and MCP servers.

## Included

- Core scoring and comparison engine
- Read-only MCP tools and `search`/`fetch` compatibility wrappers
- REST API and OpenAPI spec
- Hugging Face demo draft
- Hugging Face dataset draft
- Source-traced Official MCP Registry metadata candidates
- Reports, evals, release pack, and manual launch workspace

## Real Data Scope

- `mcp_registry`: 50 registry metadata objects
- `public_beta_mcp`: 50 registry metadata candidates
- Source traces: 191
- Raw payload mode: `manual_raw`

## Run Locally

```powershell
python -m ai_objective_index.api
python -m ai_objective_index.mcp_smoke
python hf_demo/app.py
python -m ai_objective_index.datascope_qa
```

## Boundary

AOI is read-only. It is not a quality guarantee, not security certification, not purchasing advice, and not an official standard.

AOI does not buy, book, pay, log in, send email, submit forms, purchase, connect accounts, verify suppliers, or sign contracts.

## Private Deployment Links

- GitHub private staging repo: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space, private: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset, private: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample
- MCP Registry submission: HOLD, manual only.

These links are private deployment links unless the owner manually changes visibility. They are not a public release claim. `public_beta_mcp` records are source-traced registry metadata candidates; they are not verified, not safe/certified, not security certified, not a quality guarantee, and not purchasing advice.
