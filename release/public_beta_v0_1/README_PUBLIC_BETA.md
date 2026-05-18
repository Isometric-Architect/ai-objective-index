# AI Objective Index Public Beta v0.1

AI Objective Index (AOI) is a read-only MCP/API benchmark and objective comparison engine for AI tools, APIs, SaaS products, and MCP servers.

## Current Scope

- AI tools / APIs / SaaS / MCP servers
- Local sample records
- Local generated fixture extraction records
- Integrated sample + generated scope
- Manual curated records
- Official MCP Registry intake records in offline fixture or explicit live mode

## Data Scopes

- `sample`: default sample records
- `generated`: local fixture extraction records, `EXTRACTED_UNVERIFIED`
- `integrated`: sample + generated records
- `curated`: manually curated candidates
- `public_beta`: curated candidates that pass the evidence gate
- `mcp_registry`: local Official MCP Registry intake records
- `public_beta_mcp`: calibrated registry metadata candidates; not verified or security certified; may be empty in fixture mode

## Run Local API

```powershell
python -m ai_objective_index.api
```

## Run MCP Smoke

```powershell
python -m ai_objective_index.mcp_smoke
```

## Run Hugging Face Demo Locally

```powershell
python hf_demo/app.py
```

## Run Eval And Reports

```powershell
python -m ai_objective_index.eval_runner
python -m ai_objective_index.report_generator
```

## Boundary

AOI is read-only. It is not a quality guarantee, official standard, legal advice, financial advice, medical advice, purchasing advice, procurement advice, compliance certification, or safety certification.

AOI does not broadly crawl live sites, scrape arbitrary pages, follow links, call external LLM APIs, buy, book, pay, log in, send email, submit forms, purchase, connect accounts, verify suppliers, or sign contracts. Official MCP Registry live intake, if used, requires explicit `--allow-network`.
