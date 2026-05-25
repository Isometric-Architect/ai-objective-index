# DataCapsule-7 Operator Runbook

DataCapsule-7 provides an opt-in workflow artifact template. It is not active in this repository by default.

## How To Use

1. Review `examples/datacapsule7_repository_manifest_workflow.yml`.
2. Copy it into `.github/workflows/` only in a repository where the owner wants the workflow enabled.
3. Provide a committed CSV, JSONL, or JSON corpus manifest path when manually dispatching the workflow.
4. Download the generated JSON/Markdown artifact and review HOLD/BLOCK items before using the related corpus.

## Boundaries

- The template uses `workflow_dispatch`, not automatic PR posting.
- The template uploads local review artifacts; it does not post comments.
- DataCapsule does not crawl directories, inspect private file contents, fetch URLs, call GitHub APIs, call external services, handle tokens, prove rights, certify privacy, guarantee data quality, prove evaluation cleanliness, clear licenses, provide purchasing advice, or authorize actions.
- Keep private rights analysis, receipt weighting, private negative-control banks, private probe seeds, commercial data policy, and enterprise data policy outside public artifacts.
