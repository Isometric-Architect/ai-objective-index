# Package 6D DataScope QA

Package 6D hardens AOI's data scope path across local Core, MCP tools, REST API, OpenAPI, Hugging Face demo, examples, evals, reports, and docs.

It adds:

- `src/ai_objective_index/datascope_qa.py`
- `src/ai_objective_index/beta_readiness.py`
- `data/generated/datascope_qa_results_v0_2.json`
- `data/generated/beta_readiness_report_v0_2.md`

Run:

```powershell
python -m ai_objective_index.datascope_qa
python -m ai_objective_index.beta_readiness
```

The QA output checks:

- object count;
- trace count;
- searchable object count;
- average score over fixed queries;
- status counts;
- object types;
- missing-field count;
- source trace coverage;
- top result names by query;
- generated status discipline;
- errors.

## Intentionally Not Implemented

Package 6D does not implement live crawling, network fetch, external LLM APIs, Hugging Face publishing, community posting, payment, booking, login, email sending, form submission, purchase, contract signing, account connection, supplier claim/verify, or profile modification.

Generated data remains `EXTRACTED_UNVERIFIED`. Productization Mode allows implementation and beta-readiness checks, but product claims require product evidence.
