# Package 8G: Hugging Face Private Upload

Package 8G adds a private-only Hugging Face upload helper for the AOI Space and Dataset bundles.

It uses the local Hugging Face CLI/API only if the environment is already authenticated. It must not ask for tokens in chat, print tokens, store tokens, commit tokens, make repositories public, post to communities, submit to MCP Registry, crawl, scrape, or perform external actions.

## Commands

```powershell
python -m ai_objective_index.hf_auth_check
python -m ai_objective_index.hf_private_upload --dry-run
python -m ai_objective_index.hf_private_upload --execute
python -m ai_objective_index.hf_post_upload_qa
```

Default behavior is dry-run. `--execute` creates/uploads only if local Hugging Face authentication is already available.

## Targets

- Space: `edict-lab/ai-objective-index-demo`
- Dataset: `edict-lab/ai-objective-index-sample`
- Visibility: private
- Space SDK: Gradio

