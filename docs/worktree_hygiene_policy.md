# Worktree Hygiene Policy

Do not use `git add .` during public operations.

AOI has many generated outputs from release, registry, Hugging Face, and report workflows. Package 8M classifies them instead of deleting or committing them automatically.

## Classification Buckets

- `safe_package_8m_files`: files created by the current package.
- `likely_generated_outputs`: generated reports, registry outputs, Hugging Face bundle copies, and other reproducible outputs.
- `safe_to_commit_later`: docs and public launch records that may be committed after review.
- `should_ignore`: caches, logs, pyc files, temp dirs, and local scratch.
- `requires_user_review`: raw payloads, dist archives, large files, or unexpected paths.
- `do_not_commit`: token, credential, password, secret, private key, or environment files.

## Rules

- Do not delete files without explicit review.
- Do not commit raw payloads or dist archives casually.
- Treat `do_not_commit` as blocking.
- Use focused staging lists for each package.

