# DataCapsule Repository Audit Limitations

DataCapsule repository audit reports are local artifact summaries. They help a maintainer inspect data-use metadata, but they are not legal review, privacy review, data-quality review, or evaluation-cleanliness proof.

## What The Report Can Say

- which local fixtures or repository-supplied metadata artifacts were reviewed
- which requested use classes were represented
- which items were `ALLOW_USE`, `HOLD_*`, or `BLOCK_*`
- which negative-control outcomes were recorded
- whether false-pass count was zero for the local public fixture set

## What The Report Must Not Say

- Do not say legal sufficiency is confirmed.
- Do not say privacy compliance is certified.
- Do not say data quality is guaranteed.
- Do not say a license has been cleared.
- Do not say evaluation cleanliness is proven.
- Do not say purchasing is recommended.
- Do not say external actions are authorized.

## Operational Boundary

The report is a draft review artifact. Posting it to a pull request, enabling a workflow, crawling a repository, reading private file contents, fetching live sources, calling external services, or authorizing data use requires a separate explicit owner action.
