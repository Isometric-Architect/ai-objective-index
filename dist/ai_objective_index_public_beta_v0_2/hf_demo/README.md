# AI Objective Index Hugging Face Demo

This is a local Hugging Face Space draft for AI Objective Index (AOI). It demonstrates read-only objective-fit ranking for sample AI tools, APIs, SaaS products, and MCP servers.

## Run Locally

```bash
pip install -r hf_demo/requirements.txt
python hf_demo/app.py
```

If Gradio is not installed, `app.py` remains import-safe and prints a clear install message.

## Current Scope

- AI tools
- APIs
- SaaS products
- MCP servers

## Read-Only Warning

The demo uses local sample/extracted records only. It does not crawl the web, log in, send email, submit forms, modify accounts, book, pay, purchase, or sign contracts.

AOI output is not a quality guarantee. It is not legal, financial, medical, purchasing, procurement, compliance, or professional advice.

## Data Scope

The demo supports:

- `sample`: default Package 0/1 sample records
- `generated`: local Package 6A fixture extraction records
- `integrated`: sample + generated records
- `curated`: manually curated candidates
- `public_beta`: curated candidates that pass the evidence gate
- `mcp_registry`: local Official MCP Registry intake records
- `public_beta_mcp`: registry records that pass the calibrated candidate gate

Generated, curated, and registry records remain `EXTRACTED_UNVERIFIED`. `public_beta_mcp` candidates are registry metadata candidates, not verified servers, security certification, quality guarantees, purchasing advice, or action permission. `public_beta` and `public_beta_mcp` may return warnings if no object is ready. The demo never runs live registry intake or network fetch. Productization Mode allows this demo to be built and tested, but public product claims require product evidence.

For the v0.2 real-data public beta pack, `public_beta_mcp` may contain Official MCP Registry metadata candidates processed from local raw JSON. These candidates are still not verified, not security certified, not quality guaranteed, and not action-ready.
