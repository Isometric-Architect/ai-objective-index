# Package 8H: Private Deployment Sync

Package 8H binds the real private deployment links into local AOI materials and verifies private staging status.

Commands:

```powershell
python -m ai_objective_index.deployment_link_sync
python -m ai_objective_index.private_deployment_qa
python -m ai_objective_index.hf_github_crosslink_audit
python -m ai_objective_index.deployment_push_sync --dry-run
python -m ai_objective_index.deployment_push_sync --execute
```

Deployment links:

- GitHub private repo: https://github.com/Isometric-Architect/ai-objective-index
- Hugging Face Space, private: https://huggingface.co/spaces/edict-lab/ai-objective-index-demo
- Hugging Face Dataset, private: https://huggingface.co/datasets/edict-lab/ai-objective-index-sample

Package 8H does not make anything public, create a GitHub release, post to communities, submit to MCP Registry, crawl, scrape, follow links, call external LLM APIs, or execute external actions.

`public_beta_mcp` remains a source-traced registry metadata candidate set. It is not verified, not security certified, not a quality guarantee, not purchasing advice, and not action permission.
