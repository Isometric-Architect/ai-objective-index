# Public Metrics Baseline

Public beta metrics should be interpreted gently.

Useful signals:

- GitHub issues.
- GitHub stars.
- GitHub clones/downloads if visible.
- Hugging Face Space runs.
- Hugging Face Dataset downloads.
- Failed query reports.
- Missing source trace reports.
- Install failures.

Quiet signal is not failure. No immediate traction does not mean failure. The first public goal is to verify that links, docs, demos, and issue templates work.

Package 8N writes the first active metrics snapshot to:

- `public_ops/observation/OBSERVATION_SNAPSHOT_0H.json`
- `public_ops/observation/PUBLIC_METRICS_SNAPSHOT_0H.md`

Online fields may be `not_checked` if GitHub or Hugging Face API checks are unavailable. That is acceptable for observation and should not be interpreted as a product failure.
