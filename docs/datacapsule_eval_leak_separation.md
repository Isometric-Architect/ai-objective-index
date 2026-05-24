# DataCapsule Eval-Leak Separation

DataCapsule eval-leak separation is a local metadata check. It compares file paths marked for `train` and `evaluate` or `eval` purposes in a repository-supplied manifest.

The check can:

- pass when train and evaluation paths are separated in local metadata;
- hold when purpose fields are missing or a row explicitly marks eval-leak risk;
- block when the same local path is declared for both train and evaluation use.

The check cannot prove evaluation cleanliness. It does not inspect file contents, compare semantic similarity, crawl history, fetch remote sources, validate dataset lineage, or certify benchmark integrity.

Current labels:

- `PASS_EVAL_SEPARATION_LOCAL_METADATA`
- `HOLD_EVAL_LEAK_REVIEW`
- `BLOCK_EVAL_LEAK_CONFLICT`

These labels are review aids only. A pass means the supplied local manifest did not show direct train/eval path overlap; it is not evidence that a dataset is uncontaminated.
