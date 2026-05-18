# Real MCP Integration

Package 7A adds real MCP SDK integration hooks while preserving AOI's read-only and local-data-only boundary.

## What Package 7A Adds

- `mcp_compat.py`: generic read-only `search` and `fetch` wrappers for MCP clients that expect those tool names.
- `mcp_runtime.py`: optional FastMCP runtime builder when the MCP Python SDK is installed.
- `mcp_stdio_entrypoint.py`: stdio entrypoint for local MCP clients.
- `mcp_smoke.py`: local smoke check that does not require the MCP SDK.

All tools reuse the existing AOI MCP/core functions. They do not duplicate scoring, search, comparison, source trace, or missing-field logic.

## Run The Stdio Entrypoint

```powershell
python -m ai_objective_index.mcp_stdio_entrypoint
```

If the MCP SDK is not installed, the command prints:

```text
MCP SDK not installed. Use mcp_tools functions, manifest, or install optional dependency.
```

## Optional MCP SDK Install

```powershell
pip install "ai-objective-index[mcp]"
```

or install the SDK directly:

```powershell
pip install mcp
```

The normal AOI test suite does not require the MCP SDK.

## Smoke Test

```powershell
python -m ai_objective_index.mcp_smoke
```

The smoke test calls local `search` and `fetch`, confirms no forbidden actions are exposed as tools, and writes `data/generated/mcp_smoke_result_v0_2.json`.

## Read-Only Boundary

Package 7A does not crawl, fetch network data, call external LLM APIs, publish, post, pay, book, log in, email, submit forms, purchase, connect accounts, verify suppliers, or sign contracts.
