# QIRA-9 Operator Runbook

QIRA-9 provides an opt-in workflow artifact template. It is not active in this repository by default.

## How To Use

1. Review `examples/qira9_optional_pr_review_artifact_workflow.yml`.
2. Copy it into `.github/workflows/` only in a repository where the owner wants the workflow enabled.
3. Provide a committed QIRA task packet path when manually dispatching the workflow.
4. Download the generated JSON/Markdown artifact and review HOLD/BLOCK items before using the related patch.

## Boundaries

- The template uses `workflow_dispatch`, not automatic PR posting.
- Repository-owned CI may run the listed checks only after a repository owner enables the template.
- QIRA does not post comments, call GitHub APIs on behalf of QIRA, apply patches, merge, deploy, upload packages, publish registry metadata, handle tokens, certify security, guarantee quality, prove product readiness, or grant authorization for external actions.
- Keep private thresholds, anti-gaming rules, private negative controls, private probe seeds, and commercial policy outside public artifacts.
