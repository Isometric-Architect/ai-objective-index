# Package 8P: MCP Registry PyPI Readiness

Package 8P prepares AOI for a future PyPI-based MCP Registry submission path.

Run:

```powershell
python -m ai_objective_index.package_metadata_audit
python -m ai_objective_index.pypi_publish_readiness
python -m ai_objective_index.mcp_registry_pypi_builder
python -m ai_objective_index.mcp_registry_publish_readiness
python -m ai_objective_index.pypi_upload_instructions
python -m ai_objective_index.community_manual_queue
```

Package 8P does not upload to PyPI or TestPyPI, submit to MCP Registry, broaden Hugging Face token scopes, post to communities, crawl, scrape, call external LLM APIs, print/store tokens, force push, or perform real-world actions.

MCP Registry submission remains HOLD until the PyPI package is actually public, server metadata matches the README `mcp-name` marker, and publisher/auth requirements pass.
