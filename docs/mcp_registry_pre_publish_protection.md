# MCP Registry Pre-Publish Protection

Run the technology protection gate before MCP Registry publication:

```powershell
python -m ai_objective_index.tech_protection_audit
python -m ai_objective_index.public_private_split_audit
python -m ai_objective_index.package_artifact_exposure_audit
python -m ai_objective_index.anti_clone_risk_audit
python -m ai_objective_index.license_ip_positioning_audit
python -m ai_objective_index.mcp_registry_pre_publish_protection_gate
```

MCP Registry publication increases discoverability. It is still only a metadata listing. It does not certify security, verify quality, establish product readiness, provide purchasing advice, or authorize actions.

Do not expose private scoring logic in registry metadata. Keep exact weights, thresholds, provider priors, anti-gaming rules, private negative-control seeds, private probe banks, and commercial routing policies out of public files.

After this gate is PASS, Package 8R-B can attempt publisher setup, GitHub auth, dry-run, and guarded submit. The submit step still requires `AOI_MCP_REGISTRY_SUBMIT_CONFIRM=YES`.
