# Package 9B Capability Trust Schema MVP

Package 9B turns the Package 9A vNext cards into a minimal local capability trust model.

It adds deterministic offline models for:

- `CapabilityTrustCard`
- `CapabilityEvidenceSummary`
- `ObjectiveCapabilityMatch`
- `CapabilityRiskBoundary`
- `CapabilityRouteDecision`
- `CapabilityTrustProfile`
- `CapabilityTrustReport`

The model estimates route readiness for a capability candidate relative to an objective. It does not verify the capability, certify security, guarantee quality, or grant action permission.

Run:

```bash
python -m ai_objective_index.vnext.trust_cli --query "find MCP servers for browser automation" --objective "select source-traced MCP candidates" --data-scope public_beta_mcp --limit 5
python -m ai_objective_index.vnext_capability_trust_audit
```

Package 9B remains local and offline. It does not run probes, execute a gateway, scan live systems, upload to PyPI, submit to MCP Registry, or post to communities.
