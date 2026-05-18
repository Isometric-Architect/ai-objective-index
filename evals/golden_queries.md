# Golden Queries

AOI golden queries are read-only benchmark prompts used to exercise objective-fit search and scoring.

## How To Run

```powershell
python -m ai_objective_index.eval_runner
```

## Queries

| query_id | domain | query | structural_pass | relevance_pass |
| --- | --- | --- | --- | --- |
| golden-001 | ai_tools | Find a cheap image generation API with commercial-use terms. | True | True |
| golden-002 | mcp_servers | Compare MCP servers for browser automation. | True | True |
| golden-003 | ai_saas | Find AI coding tools with clear pricing and docs. | True | True |
| golden-004 | mixed_ai_tools | Find open-source agent frameworks with active repos. | True | True |
| golden-005 | ai_apis | Find AI APIs with free tiers and clear rate limits. | True | True |
| golden-006 | ai_apis | Rank OCR APIs for scanned PDF table extraction under a low monthly budget. | True | True |
| golden-007 | ai_saas | Compare meeting transcription tools that provide speaker labels and action items. | True | True |
| golden-008 | ai_tools | Find an LLM gateway with budget controls and provider fallback routing. | True | True |
| golden-009 | ai_apis | Find a speech synthesis API with commercial audio usage terms. | True | True |
| golden-010 | ai_saas | Compare workflow automation tools that include AI steps and human approvals. | True | True |
| golden-011 | ai_tools | Find a vector database with free development tier and hybrid search. | True | True |
| golden-012 | ai_apis | Find a document extraction API with JSON output and retention controls. | True | True |
| golden-013 | ai_saas | Compare AI video generation tools for commercial social media exports. | True | True |
| golden-014 | ai_apis | Find an AI search API that returns citations and supports freshness filters. | True | True |
| golden-015 | ai_apis | Find a low-cost embedding API for multilingual RAG. | True | True |
| golden-016 | ai_tools | Find a local LLM app that keeps documents on device by default. | True | True |
| golden-017 | ai_saas | Compare prompt management tools with versioning and eval runs. | True | True |
| golden-018 | mixed_ai_tools | Find open-source RAG frameworks with ingestion and retrieval evaluation. | True | True |
| golden-019 | ai_saas | Find a data labeling platform for RLHF preference tasks. | True | True |
| golden-020 | ai_saas | Find an AI monitoring tool for LLM traces, cost dashboards, and drift alerts. | True | True |
| golden-021 | mixed_ai_tools | List options with missing policy fields for commercial deployment review. | True | True |
| golden-022 | mixed_ai_tools | Explain why a cheap embedding option ranks above a broader LLM gateway for RAG. | True | True |
| golden-023 | ai_apis | Generate a read-only decision receipt for choosing an OCR API. | True | True |
| golden-024 | mcp_servers | Compare web search MCP and browser automation MCP tools without triggering login or form submission. | True | True |
