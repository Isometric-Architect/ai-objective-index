# QIRA Workflow Opt-In Runbook

Use this runbook only when a repository owner wants QIRA review artifacts from normal CI.

1. Read `examples/qira9_optional_pr_review_artifact_workflow.yml`.
2. Confirm the task packet input path points to committed repository metadata.
3. Copy the example into `.github/workflows/` only after owner approval.
4. Run the workflow manually with `workflow_dispatch`.
5. Download the generated artifact.
6. Review every HOLD/BLOCK item before using the related patch.

The workflow template is intentionally conservative. It uploads local JSON/Markdown artifacts and does not post PR comments, grant elevated permissions, merge, deploy, publish packages, or authorize actions.

Do not paste tokens into workflow files, issue comments, pull requests, or chat. Do not expose private kernel values in repository artifacts.
