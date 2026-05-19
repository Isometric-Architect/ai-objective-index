# Package 8D: GitHub Private Staging QA

Package 8D verifies the private GitHub staging repository, binds the real GitHub repository URL into local release materials, and prepares a manual public-switch checklist.

It does not make the repository public. It does not create a GitHub release, upload to Hugging Face, post to communities, submit to MCP Registry, crawl, scrape, follow links, or perform external actions.

## Commands

```powershell
python -m ai_objective_index.github_post_upload_qa
python -m ai_objective_index.github_link_binder
python -m ai_objective_index.public_switch_preflight
```

## Boundary

The repository remains private staging unless the user manually changes visibility in GitHub. A PASS from public switch preflight means the materials are locally ready for human review; it is not product readiness, supplier verification, security certification, quality guarantee, purchasing advice, or action permission.

