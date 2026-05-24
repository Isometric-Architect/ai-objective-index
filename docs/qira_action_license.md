# QIRA Action License

The QIRA action license maps a patch receipt to action boundaries.

| Action | Meaning |
| --- | --- |
| `patch_draft` | Whether the patch can be kept as a local draft artifact |
| `pr_open` | Whether the patch can be considered for PR-level review |
| `merge` | Whether merge evidence is sufficient |
| `deploy` | Whether deploy evidence is sufficient |
| `public_claim` | Whether a scoped public/internal claim can be made |

QIRA-1 defaults deploy to `BLOCK`. Merge remains `HOLD` even when scoped local fixture evidence passes, because merge requires project-specific review and integration evidence.

The license is not a legal license, security certification, quality guarantee, or deployment approval. It is a conservative action-boundary receipt.
