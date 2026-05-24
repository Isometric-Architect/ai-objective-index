# QIRA-8 PR Artifact Bundle

QIRA-8 converts local QIRA packet, CI evidence, validation, bridge, and review artifacts into reviewer-facing files:

- Markdown reviewer report;
- PR comment draft;
- artifact manifest with paths, sizes, and SHA-256 hashes;
- bundle result JSON.

The package is local and read-only. It does not post comments, call GitHub APIs, execute project commands, apply patches, merge, deploy, upload packages, publish registry metadata, or handle tokens.

## Command

```powershell
python -m ai_objective_index.qira.reviewer_report --run-sample
```

By default the sample regenerates QIRA-7 pass artifacts first, then writes QIRA-8 outputs under `public_launch/qira8/`.

## Outputs

- `QIRA8_REVIEWER_REPORT.md`
- `QIRA8_PR_COMMENT_DRAFT.md`
- `QIRA8_ARTIFACT_MANIFEST.json`
- `QIRA8_BUNDLE_RESULT.json`
- `QIRA8_NEXT_STEPS.md`

## Intended Use

In an opt-in workflow, a repository owner can upload these files as workflow artifacts. A later package may add an explicit PR-comment posting gate, but QIRA-8 only writes a draft.

The reviewer report explains action-license boundaries. A scoped QIRA pass may support patch draft or PR review under recorded evidence, while merge, deploy, package upload, registry submission, and public readiness remain separately gated.
