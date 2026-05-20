# Package 8O: Public Beta Launch Wave 1

Package 8O creates the first public beta launch wave: a GitHub prerelease, conservative feedback drafts, optional authenticated discussion posting, and an MCP Registry eligibility gate.

Run dry-runs first:

```powershell
python -m ai_objective_index.github_release_manager --dry-run
python -m ai_objective_index.community_launch_manager --dry-run
python -m ai_objective_index.mcp_registry_server_json_builder
python -m ai_objective_index.mcp_registry_submission_gate --dry-run
python -m ai_objective_index.launch_wave1_report
```

Execute GitHub release only after dry-run passes:

```powershell
python -m ai_objective_index.github_release_manager --execute
```

Execute safe discussion posting only when local authenticated tooling supports it:

```powershell
python -m ai_objective_index.community_launch_manager --execute-safe
```

MCP Registry submission remains gated. It must not run unless eligibility is `PASS_SUBMIT_READY` and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set.

Package 8O does not post to HN, Reddit, OpenAI Developer Community, Product Hunt, or MCP communities automatically. It does not create verified/safe/security-certified/quality-guaranteed claims.
