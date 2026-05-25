# AgentSec-6 Manifest Corpus Ingestion

AgentSec-6 adds local manifest corpus ingestion for repository-supplied MCP/tool metadata. It reads a JSON manifest object, a JSON list, a `{"manifests": [...]}` corpus file, or a local directory of JSON manifests, then reuses the existing AgentSec scanner and public policy gate to produce a corpus-level artifact.

Run:

```powershell
python -m ai_objective_index.agentsec.corpus_ingest --run-sample
python -m ai_objective_index.agentsec.package6
python -m ai_objective_index.agentsec_claim_audit
```

Generated outputs:

- `public_launch/agentsec6/AGENTSEC6_SAMPLE_MANIFEST_CORPUS.json`
- `public_launch/agentsec6/AGENTSEC6_CORPUS_INTAKE_RESULT.json`
- `public_launch/agentsec6/AGENTSEC6_POLICY_GATE_RESULT.json`
- `public_launch/agentsec6/AGENTSEC6_CORPUS_REPORT.md`
- `public_launch/agentsec6/AGENTSEC6_PACKAGE_RESULT.json`
- `public_launch/agentsec6/AGENTSEC6_NEXT_STEPS.md`
- `public_launch/agentsec6/AGENTSEC_CLAIM_BOUNDARY_AUDIT.json`

## Boundary

AgentSec-6 is local/offline metadata review only. It does not call live MCP servers, execute tools, fetch URLs, handle tokens, certify security, guarantee quality, prove product readiness, provide live gateway protection, or authorize external actions.
