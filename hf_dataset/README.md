# Dataset Card: ai-objective-index-sample

## Dataset Name

`ai-objective-index-sample`

## Scope

This local dataset draft contains AOI sample/extracted benchmark records and, when available, `public_beta_mcp` Official MCP Registry metadata candidates.

## Real Registry Candidate Files

- `mcp_registry_beta_candidates.jsonl`: `public_beta_mcp` registry metadata candidates.
- `mcp_registry_source_traces.jsonl`: source traces derived from registry metadata.

Current local counts:

- MCP registry objects: `50`
- Source traces: `191`
- `public_beta_mcp` candidates: `50`

## Source Trace Explanation

`SourceTrace` links a field to a source URL, title, snippet, retrieval timestamp, and confidence value. A trace supports a field, but it does not prove completeness, currentness, legality, safety, or quality.

## Intended Use

Benchmarking and testing objective ranking for AI tools/APIs/SaaS/MCP servers.

## Not Intended For

This dataset is not intended for automated purchase, legal decisions, financial decisions, medical decisions, safety certification, security certification, or quality guarantees.

## Limitations

Registry candidates are not verified, not security certified, not quality guaranteed, and not purchasing advice. This dataset is not a quality guarantee. This repository does not automatically publish to Hugging Face.

## Private Deployment Links

- GitHub private staging repo: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space, private: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset, private: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample
- MCP Registry submission: HOLD, manual only.

These links are private deployment links unless the owner manually changes visibility. They are not a public release claim. `public_beta_mcp` records are source-traced registry metadata candidates; they are not verified, not safe/certified, not security certified, not a quality guarantee, and not purchasing advice.
