# MCP Registry PyPI Path

MCP Registry can reference a PyPI package with `registryType: pypi`.

Package 8P prepares:

- README marker: `<!-- mcp-name: io.github.Isometric-Architect/ai-objective-index -->`
- `.mcp/server.json`
- package identifier: `ai-objective-index`
- version: `0.3.0a1`
- transport: `stdio`

Submission is not automatic. The package must first be uploaded and verified on PyPI. Then run:

```powershell
python -m ai_objective_index.mcp_registry_publish_readiness
```

Only submit later if readiness is `PASS_READY_TO_SUBMIT` and explicit confirmation is present.

Package 8Q-A can create local dist files and run `twine check`. MCP Registry readiness should still HOLD until the package is actually uploaded to PyPI and registry tooling/authentication pass.

Package 9F keeps MCP Registry submission gated after vNext. `.mcp/server.json` now describes the Objective Router, ExecutionReceipt memory, and local Probe-before-Use surfaces, but Registry submission still waits for a final package version decision, a real PyPI package, and explicit submit confirmation.

Package 8Q-A resumed applies `0.3.0a1` for the local build candidate. MCP Registry remains HOLD until TestPyPI/PyPI verification is complete and explicit submission confirmation exists.
## After Real PyPI Direct Upload

Package 8Q-C-alt can verify a real PyPI `0.3.0a1` upload when TestPyPI is unavailable. MCP Registry submission still waits for:

- real PyPI upload confirmation;
- real PyPI install verification;
- `.mcp/server.json` `registryType: pypi` metadata;
- README `mcp-name` marker match;
- no secrets or overclaims;
- `mcp-publisher` availability and registry auth in a later package.

Run:

```powershell
python -m ai_objective_index.mcp_registry_after_pypi_gate
```

Do not submit to MCP Registry from Package 8Q-C-alt.

## Package 8R Publisher Gate

Package 8R starts from the verified real PyPI package and audits `.mcp/server.json` as a final `registryType: pypi` manifest. The expected server name is `io.github.Isometric-Architect/ai-objective-index`, and the package identifier/version are `ai-objective-index` / `0.3.0a1`.

Run:

```powershell
python -m ai_objective_index.mcp_publisher_setup --check
python -m ai_objective_index.mcp_registry_manifest_final_audit
python -m ai_objective_index.mcp_registry_publish_runner --dry-run
```

Do not publish unless `mcp-publisher` is available, GitHub auth is complete, the manifest audit passes, and `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` is set.
