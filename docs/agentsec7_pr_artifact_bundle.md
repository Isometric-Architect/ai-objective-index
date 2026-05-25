# AgentSec-7 PR Artifact Bundle

AgentSec-7 turns local AgentSec-6 manifest-corpus outputs into reviewer-facing artifacts:

- Markdown reviewer report
- PR comment draft
- artifact manifest with hashes
- bundle result JSON
- next-step note

The package is local and read-only. It does not call live MCP servers, execute tools, fetch URLs, call GitHub APIs, post comments, handle tokens, certify security, guarantee quality, prove product readiness, or authorize external actions.

## Inputs

AgentSec-7 reads AgentSec-6 public outputs under `public_launch/agentsec6/`:

- `AGENTSEC6_SAMPLE_MANIFEST_CORPUS.json`
- `AGENTSEC6_CORPUS_INTAKE_RESULT.json`
- `AGENTSEC6_POLICY_GATE_RESULT.json`
- `AGENTSEC6_CORPUS_REPORT.md`
- `AGENTSEC6_PACKAGE_RESULT.json`

The default CLI regenerates the safe local sample before writing AgentSec-7 outputs.

## Command

```bash
python -m ai_objective_index.agentsec.reviewer_bundle --run-sample
```

Use `--no-upstream-sample` to build from existing local AgentSec-6 files.

## Public Boundary

AgentSec-7 may summarize supplied metadata and route labels such as `ALLOW_METADATA_ONLY`, `HOLD_REVIEW_REQUIRED`, and `BLOCK_POLICY_RISK`.

AgentSec-7 must not expose exact private thresholds, provider priors, anti-gaming rules, private negative-control banks, private probe seeds, or commercial routing policy.
