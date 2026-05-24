# QIRA-4 GitHub Action Dry Run

QIRA-4 adds a reusable GitHub Action wrapper:

```text
.github/actions/qira-releasegate-dry-run/action.yml
```

The action calls:

```powershell
python -m ai_objective_index.qira.github_action --input <packet.json> --output-dir public_launch/qira4
```

It reads a local QIRA task packet and writes a release-gate dry-run result. It does not apply patches, execute project test commands, deploy code, contact external services, request tokens, or publish anything.

The repository does not enable an automatic workflow in this package. A sample workflow lives at:

```text
examples/qira_releasegate_dry_run_workflow.yml
```

Copy it into `.github/workflows/` only when the repository owner intentionally wants to enable it.
