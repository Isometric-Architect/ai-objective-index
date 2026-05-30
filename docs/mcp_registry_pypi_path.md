# MCP Registry PyPI Path

MCP Registry can reference a PyPI package with `registryType: pypi`.

Package 8P prepares:

- README marker: `<!-- mcp-name: io.github.Isometric-Architect/ai-objective-index -->`
- `.mcp/server.json`
- package identifier: `ai-objective-index`
- current recovery version: `0.3.0a2`
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

## AOI 0.3.0a2 Marker-Sync Recovery

The 0.3.0a1 artifact remains published and should not be overwritten or yanked. AOI 0.3.0a2 is the recovery package for synchronizing the PyPI README marker with `.mcp/server.json`:

- server name: `io.github.Isometric-Architect/ai-objective-index`
- package: `ai-objective-index`
- package version: `0.3.0a2`
- registry type: `pypi`

Run the recovery helpers:

```powershell
python -m ai_objective_index.aoi_030a2_marker_sync
python -m ai_objective_index.aoi_030a2_build_verify
python -m ai_objective_index.aoi_030a2_pypi_upload_gate
python -m ai_objective_index.aoi_030a2_pypi_verify
python -m ai_objective_index.aoi_mcp_registry_recovery_gate
```

Real PyPI upload requires `AOI_REAL_PYPI_UPLOAD_CONFIRM=YES` and an interactive twine token prompt. MCP Registry publish requires `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES` after PyPI verification and local `mcp-publisher validate` pass.

## Agent Adoption Before Upload

AOI-AGENT-ADOPTION-2 added the read-only agent REST/MCP surfaces and package-data inclusion audit for `0.3.0a2`. The final PyPI and MCP Registry path now uses:

```powershell
python -m ai_objective_index.aoi_030a2_final_preflight
python -m ai_objective_index.aoi_030a2_build_verify
python -m ai_objective_index.aoi_030a2_final_pypi_upload_gate
```

Real PyPI upload remains explicit:

```powershell
$env:AOI_REAL_PYPI_UPLOAD_CONFIRM="YES"
python -m ai_objective_index.aoi_030a2_final_pypi_upload_runner --execute
python -m ai_objective_index.aoi_030a2_final_pypi_verify
```

MCP Registry publication remains explicit and happens only after PyPI verification:

```powershell
python -m ai_objective_index.aoi_030a2_final_mcp_registry_gate
$env:AOI_MCP_REGISTRY_SUBMIT_CONFIRM="YES"
python -m ai_objective_index.aoi_030a2_final_mcp_registry_publish --execute
python -m ai_objective_index.aoi_030a2_final_mcp_registry_reconcile
```

Do not overwrite or yank `0.3.0a1`, do not store tokens, do not commit `.pypirc`, dist artifacts, or `mcp-publisher`, and do not present Registry publication as security certification, product readiness, proof, quality guarantee, legal/privacy/license clearance, or action authorization.

AOI-AGENT-ADOPTION-1 keeps version `0.3.0a2` because the recovery package has not been uploaded yet. It adds agent-native discovery and preflight artifacts before the final upload path:

- capability card for ordinary AI agents;
- discover mode request/response examples;
- preflight mode request/response examples;
- claim-boundary and staleness policy artifacts;
- ResidualOps escalation map.

This does not change the canonical MCP name, package identifier, or package version. It also does not perform PyPI upload or MCP Registry publish.
