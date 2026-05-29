# ROE-9 First QIRA Pilot Receipt Packager

ROE-9 packages a local/offline QIRA-Code ReleaseGate review into a reviewer-facing pilot receipt bundle.

It shows the shape:

TaskPacket -> PatchClassification -> BehaviorContract -> CI evidence summary -> ReviewerReadout -> ReleaseGateReceipt -> FeedbackMemory.

ROE-9 does not call GitHub APIs, create PRs, post comments, mutate external repositories, merge, deploy, publish packages, execute arbitrary external commands, request tokens, or make correctness/security/product claims.

The receipt is a local review artifact with ALLOW/HOLD/BLOCK findings, evidence references, known limits, and next actions.

Commands:

```bash
python -m ai_objective_index.portfolio.qira_pilot_packager --sample
python -m ai_objective_index.portfolio.roe9_qira_pilot_gate
```
