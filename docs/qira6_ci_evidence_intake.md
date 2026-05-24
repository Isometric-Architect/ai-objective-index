# QIRA-6 CI Evidence Intake

QIRA-6 accepts externally supplied CI evidence for a QIRA task packet. It closes the gap between a generated packet and the repository's normal CI results without turning QIRA into a command runner.

QIRA-6 does not run tests. It does not call GitHub APIs, inspect live CI systems, apply patches, merge, deploy, upload packages, publish registry metadata, or handle credentials.

## Flow

```text
QIRA task packet
+ CI evidence JSON
-> command contract review
-> CI evidence validation
-> augmented QIRA task packet
-> QIRA release-gate review
```

If all supplied CI checks pass and their commands match local-safe test/static-check patterns, QIRA can mark `tests_passed=true` on the augmented packet and rerun the release-gate review. That can move a local review from `HOLD_CI_PASS_CONTRACT_GAP` to scoped contract pass.

This still does not authorize merge, deploy, package upload, registry submission, public product readiness, security certification, or quality guarantees.

## Commands

Run the bundled sample:

```powershell
python -m ai_objective_index.qira.ci_evidence_cli --run-sample
```

Review a packet and evidence file:

```powershell
python -m ai_objective_index.qira.ci_evidence_cli `
  --packet public_launch/qira5/QIRA5_GENERATED_TASK_PACKET.json `
  --evidence path\to\ci_evidence.json
```

Write sample packet/evidence templates:

```powershell
python -m ai_objective_index.qira.ci_evidence_cli --write-sample
```

## Evidence Shape

A CI evidence packet records:

- evidence source, such as `github_actions`, `local_ci`, or `manual_fixture`;
- workflow/job labels;
- check names;
- recorded command strings;
- pass/fail/skipped/unknown statuses;
- short summaries.

QIRA treats this as metadata supplied by CI or the repository owner. It does not treat the evidence as independent verification.
