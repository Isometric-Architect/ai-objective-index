# Package Artifact Exposure Policy

Before increasing distribution, inspect local and uploaded package artifacts for accidental exposure.

Audit targets:

- `dist/ai_objective_index-0.3.0a1-py3-none-any.whl`
- `dist/ai_objective_index-0.3.0a1.tar.gz`
- package metadata and include/exclude settings

Blockers:

- `.env`, `.pypirc`, tokens, credentials, or private keys;
- private kernel directories;
- private data/calibration directories;
- raw internal source masters;
- temporary virtual environments or caches;
- large residual generated outputs that are not part of the package.

If a sensitive artifact is already uploaded, do not yank/delete automatically. Prefer a remediation package: bump to the next prerelease, fix packaging, rebuild, verify, upload, then rerun the audit.
