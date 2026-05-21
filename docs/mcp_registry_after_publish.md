# MCP Registry After Publish

After MCP Registry publication, run:

```powershell
python -m ai_objective_index.mcp_registry_post_publish_verify
python -m ai_objective_index.mcp_registry_release_audit
python -m ai_objective_index.no_secrets_audit
python -m ai_objective_index.launch_claim_guard
```

Expected follow-up:

- Check that the registry entry appears after propagation.
- Keep README and `.mcp/server.json` version-aligned.
- If the version already exists, bump to the next prerelease such as `0.3.0a2`; do not delete or overwrite as a normal workflow.
- Keep public wording conservative: source-traced candidates, route decisions, known limits, and no certification claims.

Package 8S adds a protection gate before publish. If that gate is HOLD or BLOCK, resolve exposure, license, or package-artifact findings before increasing discovery through MCP Registry.

Package 8R-B adds reconcile and discovery report helpers. If publish succeeds but search is not visible yet, wait for propagation and rerun `python -m ai_objective_index.mcp_registry_submit_reconcile`.
