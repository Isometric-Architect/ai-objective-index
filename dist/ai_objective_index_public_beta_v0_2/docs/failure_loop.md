# Failure Loop

## How To Report A Failed Query

Open a `Failed query` issue and include:

- query;
- expected result;
- actual result;
- relevant object IDs;
- evidence or official source URLs;
- whether the query should become a golden query.

## How Failed Queries Become Eval Cases

Accepted failed queries are added to `data/golden_queries.json` with expected focus terms. They are then covered by `python -m ai_objective_index.eval_runner`.

## How Scoring Patches Are Documented

Scoring changes should update:

- `src/ai_objective_index/scoring.py`;
- `docs/scoring_methodology.md`;
- `evals/scoring_eval.md` after report generation;
- CHANGELOG entries for the package.

## How Source Trace Improvements Are Prioritized

Prioritize source trace improvements for:

- fields used in ranking;
- commercial-use terms;
- pricing and rate limits;
- privacy and data retention;
- documentation and API reference coverage;
- objects that appear in failed golden queries.

## v0.1 Boundary

There is no paid ranking in v0.1. AOI does not perform payment, booking, login, email sending, form submission, purchase, contract execution, account connection, supplier claim/verify, or profile modification.

