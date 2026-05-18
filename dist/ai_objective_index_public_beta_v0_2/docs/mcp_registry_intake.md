# MCP Registry Intake

Package 7D adds a narrow intake pilot for Official MCP Registry-style metadata.

Default mode is offline fixture mode:

```powershell
python -m ai_objective_index.registry_intake.mcp_registry_export --use-fixture
```

Optional live mode is explicit and limited to read-only registry API GET requests:

```powershell
python -m ai_objective_index.registry_intake.mcp_registry_export --allow-network --use-fixture false --max-servers 50
```

Package 7E adds a run wrapper that records a receipt and handles manual fallback:

```powershell
python -m ai_objective_index.registry_intake.live_registry_run
python -m ai_objective_index.registry_intake.live_registry_run --allow-network --max-servers 50
```

The default run uses no network. If `data/registry/mcp_registry_raw_v0_1.json` exists, it processes that local raw payload as `manual_raw`.

Package 7F calibrates `public_beta_mcp` as a registry metadata candidate dataset:

```powershell
python -m ai_objective_index.registry_intake.registry_beta_dataset_builder
python -m ai_objective_index.registry_intake.registry_quality_audit
python -m ai_objective_index.registry_intake.registry_beta_report_generator
```

`public_beta_mcp` candidates are not verified, not security certified, not quality guaranteed, and not action-ready.

Package 7G activates real/manual raw payloads and prevents fixture regression:

```powershell
python -m ai_objective_index.registry_intake.real_payload_activation --use-existing-raw
python -m ai_objective_index.registry_intake.registry_payload_audit
python -m ai_objective_index.registry_intake.registry_reprocess_all
```

If a real `mcp_registry_raw_v0_1.json` exists at the repository root, activation can copy it into `data/registry/` when the active registry raw file is missing or fixture-only.

Supported endpoint shape, where available:

- `GET /v0.1/servers`
- `GET /v0.1/servers/{serverName}/versions`
- `GET /v0.1/servers/{serverName}/versions/{version}`
- `latest` may be used as a version if the registry supports it.

If endpoint shape differs, the client returns a clear error or uses fixture/manual fallback. AOI does not scrape HTML or follow links.

## Manual Download Fallback

See `data/registry/mcp_registry_manual_download_instructions.md`.

## Outputs

- `data/registry/mcp_registry_raw_v0_1.json`
- `data/registry/mcp_registry_objects_v0_1.jsonl`
- `data/registry/mcp_registry_source_traces_v0_1.jsonl`
- `data/registry/mcp_registry_validation_results_v0_1.json`
- `data/registry/mcp_registry_public_beta_index_v0_1.json`
- `data/registry/mcp_registry_beta_candidates_v0_1.jsonl`
- `data/registry/mcp_registry_beta_candidate_gate_results_v0_1.json`
- `data/registry/mcp_registry_quality_audit_v0_1.json`
- `data/registry/mcp_registry_public_beta_mcp_dataset_v0_1.json`
- `data/registry/mcp_registry_beta_report_v0_1.md`
- `data/registry/real_payload_activation_result_v0_1.json`
- `data/registry/registry_payload_audit_v0_1.json`
- `data/registry/registry_reprocess_all_result_v0_1.json`

All objects remain `EXTRACTED_UNVERIFIED`.
