# AgentSec Negative Controls

AgentSec negative controls are local fake manifests that should produce conservative route outcomes.

They are used to catch regressions such as:

- forbidden action language becoming `ALLOW_METADATA_ONLY`
- unsupported verification or safety claims becoming `ALLOW_METADATA_ONLY`
- hidden instruction patterns being ignored
- official-like namespace ambiguity being treated as complete ownership evidence
- secret or exfiltration language passing without review

Run:

```powershell
python -m ai_objective_index.agentsec.negative_controls --write-sample
```

The result reports `false_pass_count`. A false pass is a local regression signal only. It is not verification, security certification, quality guarantee, live gateway protection, product-readiness proof, legal compliance, or action authorization.
