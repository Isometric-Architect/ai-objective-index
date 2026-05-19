# Package 8I: Public Launch Decision Gate

Package 8I adds a safe decision gate for a possible future public launch.

Commands:

```powershell
python -m ai_objective_index.public_launch_gate
python -m ai_objective_index.public_visibility_switch --dry-run
python -m ai_objective_index.public_launch_claim_audit
python -m ai_objective_index.private_reviewer_packager
python -m ai_objective_index.token_revocation_checklist
```

Default mode is dry-run. Actual public visibility switch requires both:

```powershell
python -m ai_objective_index.public_visibility_switch --execute
$env:AOI_PUBLIC_LAUNCH_CONFIRM="YES"
```

The execute command must not be run until the human owner has reviewed the public launch gate, claim audit, no-secrets audit, GitHub page, Hugging Face Space, and Hugging Face Dataset.

Package 8I does not post to communities, submit to MCP Registry, create a GitHub Release, crawl, scrape, follow links, call external LLM APIs, print tokens, store tokens, or force push.

PASS means the user may decide whether to switch public. It is not product readiness, security certification, supplier verification, quality guarantee, purchasing advice, or action permission.
