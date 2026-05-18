# Real Registry Payload Activation

`public_beta_mcp` can be `0` when the active registry files are fixture-mode. That is expected: fixtures are for tests and must not be promoted as real beta data.

Package 7G activates real/manual Official MCP Registry raw JSON that was saved locally from:

```text
https://registry.modelcontextprotocol.io/v0.1/servers?limit=50
```

Run:

```powershell
python -m ai_objective_index.registry_intake.real_payload_activation --use-existing-raw
python -m ai_objective_index.registry_intake.registry_reprocess_all
```

If the raw file is at the repository root as `mcp_registry_raw_v0_1.json`, activation will copy it into `data/registry/mcp_registry_raw_v0_1.json` when the current registry raw file is missing or fixture-only.

Manual or live registry metadata still maps to `EXTRACTED_UNVERIFIED`. It is not supplier verification, security certification, quality guarantee, purchasing advice, or action permission.

