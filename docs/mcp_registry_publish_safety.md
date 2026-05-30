# MCP Registry Publish Safety

MCP Registry publication should be treated as metadata distribution, not as certification.

Safe path:

1. Confirm real PyPI install verification passed.
2. Confirm `.mcp/server.json` matches `io.github.Isometric-Architect/ai-objective-index`.
3. Confirm README contains the matching `mcp-name` marker.
4. Run the manifest final audit.
5. Install and authenticate `mcp-publisher`.
6. Run dry-run first.
7. Submit only with `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.

Do not paste GitHub tokens into chat. Do not commit token files or `.pypirc`. If a credential is exposed, revoke it.

AOI remains read-only. Registry publication does not authorize payment, booking, login, email, purchase, contract signing, account connection, supplier verification, or profile modification.

## Agent Adoption Safety Note

Before `0.3.0a2` upload, AOI-AGENT-ADOPTION-1 adds discovery/preflight artifacts so ordinary AI agents can understand AOI without treating registry metadata as proof or tool availability as authorization.

The agent-facing pack is documentation, schemas, examples, and local deterministic helpers only. It does not publish to MCP Registry, run live MCP/tool calls, call external APIs, use credentials, certify security, prove correctness, claim product readiness, or authorize external actions. Private ranking weights and thresholds remain private.

## Package 8S Protection Gate

Before running a Registry submit package, run the technology protection gate:

```powershell
python -m ai_objective_index.mcp_registry_pre_publish_protection_gate
```

The gate checks whether public files and package artifacts expose private kernel details. Keep exact weights, thresholds, anti-gaming rules, provider trust priors, private negative controls, private probe seeds, and commercial routing policies outside public files.

## Package 8R-B Submit Gate

`mcp_registry_submit_execute --execute` must not run unless:

- `mcp_registry_publish_preflight` is `PASS_READY_TO_SUBMIT`;
- GitHub auth through `mcp-publisher login github` is complete;
- `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set.

Do not use GitHub PATs in chat or files.
