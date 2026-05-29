# ROE-14 Pilot Feedback and Second-Run Gate

ROE-14 adds a local/offline feedback layer for the ROE-13 dry-run. A reviewer can provide feedback on AgentSec, QIRA-Code ReleaseGate, DataCapsule, or the portfolio readout, and the system turns that feedback into a packet, deterministic classification, second-run plan, feedback memory update, and gate result.

This package does not execute the second run by default. It does not call GitHub APIs, create issues, post comments, clone repositories, fetch URLs, run live MCP/tool calls, mutate repositories, merge, deploy, publish, upload data, train models, use credentials, or make certification/proof/product-readiness claims.

## Outputs

- `pilot_feedback/PILOT_FEEDBACK_FORM_TEMPLATE.md`
- `pilot_feedback/PILOT_FEEDBACK_PACKET_SAMPLE_AGENTSEC.json`
- `pilot_feedback/PILOT_FEEDBACK_PACKET_SAMPLE_QIRA.json`
- `pilot_feedback/PILOT_FEEDBACK_PACKET_SAMPLE_DATACAPSULE.json`
- `pilot_feedback/PILOT_FEEDBACK_CLASSIFICATION_SAMPLE.json`
- `pilot_feedback/PILOT_SECOND_RUN_PLAN_SAMPLE.json`
- `pilot_feedback/PILOT_FEEDBACK_MEMORY_UPDATE_SAMPLE.json`
- `pilot_feedback/PILOT_SECOND_RUN_REVIEWER_READOUT.md`
- `public_launch/roe14/ROE14_FEEDBACK_SECOND_RUN_GATE_RESULT.json`

## Commands

```bash
python -m ai_objective_index.portfolio.pilot_feedback_form --sample
python -m ai_objective_index.portfolio.roe14_feedback_second_run_gate
```

The result is a planning artifact only. Feedback can request clarification, local evidence, fixture candidates, claim-boundary changes, or a future local second pass; it cannot authorize external action.
