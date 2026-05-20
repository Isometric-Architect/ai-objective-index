# Residual Worktree Review Policy

AOI has many generated outputs after registry, release, Hugging Face, and public operations packages. Package 8N reviews those residual changes instead of deleting them or committing them wholesale.

Rules:

- Do not run `git add .`.
- Do not delete residual files in this package.
- Treat generated leftovers as review items, not failures.
- Treat possible token, credential, `.env`, secret, password, or private-key files as blocking until reviewed.
- Treat large archives, `dist/`, and raw registry payloads as user-review items.
- Commit residual files only through future scoped packages.

The residual review writes:

- `public_ops/residual_review/RESIDUAL_WORKTREE_REVIEW_v0_1.json`
- `public_ops/residual_review/RESIDUAL_WORKTREE_REVIEW.md`
- `public_ops/residual_review/RESIDUAL_COMMIT_PLAN.md`
- `public_ops/residual_review/RESIDUAL_IGNORE_PLAN.md`
- `public_ops/residual_review/RESIDUAL_USER_REVIEW_LIST.md`
