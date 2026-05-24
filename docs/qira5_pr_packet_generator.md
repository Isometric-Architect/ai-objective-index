# QIRA-5 PR Packet Generator

QIRA-5 turns local PR-style diff text or an explicit changed-file list into a QIRA task packet. It is meant to sit between a repository's normal pull-request metadata and the existing QIRA ReleaseGate review.

The generator is local and read-only. It does not call GitHub APIs, run `git`, apply patches, execute tests, deploy code, upload packages, publish registry metadata, or handle credentials.

## Flow

```text
local diff or changed-file list
-> path classification
-> inferred behavior clauses
-> QIRA task packet
-> optional QIRA-3 review
-> ALLOW/HOLD/BLOCK action-license surface
```

## Commands

Run the bundled sample:

```powershell
python -m ai_objective_index.qira.pr_packet_cli --run-sample
```

Generate from a local diff file:

```powershell
python -m ai_objective_index.qira.pr_packet_cli `
  --diff-file path\to\pr.patch `
  --task "Add local parser support" `
  --patch-summary "Adds parser and tests" `
  --test-command "python -m pytest tests/test_parser.py"
```

Generate from a changed-file list:

```powershell
python -m ai_objective_index.qira.pr_packet_cli `
  --changed-files "src/example.py,tests/test_example.py" `
  --task "Update local example behavior"
```

## Outputs

QIRA-5 writes:

- `public_launch/qira5/QIRA5_SAMPLE_PR_DIFF.patch`
- `public_launch/qira5/QIRA5_GENERATED_TASK_PACKET.json`
- `public_launch/qira5/QIRA5_PACKET_GENERATION_RESULT.json`
- `public_launch/qira5/QIRA5_REVIEW_RESULT.json`
- `public_launch/qira5/QIRA5_NEXT_STEPS.md`

## Claim Boundary

A generated packet is an intake artifact, not verification. A listed test command is recorded for reviewer or CI use, but QIRA-5 does not execute it. A review may allow draft or PR handling under limits, but merge, deploy, package upload, registry submission, product readiness, and public claims remain separately gated.
