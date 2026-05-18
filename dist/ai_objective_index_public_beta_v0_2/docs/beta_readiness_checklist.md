# Beta Readiness Checklist

Package 6D checks local beta readiness without asserting public release certification.

Checklist:

- local tests pass;
- `python -m ai_objective_index.datascope_qa` runs;
- `sample`, `generated`, and `integrated` scopes are present;
- source trace coverage is computed for every scope;
- generated objects remain `EXTRACTED_UNVERIFIED`;
- `/status` reports scope counts, default scope, read-only status, and no live network;
- MCP manifest includes data scope support;
- Hugging Face demo is import-safe and data-scope aware;
- eval/report artifacts exist or are clearly held;
- no live network is used;
- no forbidden actions are implemented;
- Productization Mode docs exist and public claims remain evidence-gated.

Readiness tokens:

- `PASS`: condition is satisfied by local evidence.
- `HOLD`: condition needs more local evidence before beta distribution.
- `BLOCK`: condition violates a forbidden boundary.
- `NOT_CHECKED`: condition has not been evaluated.

Beta readiness is conservative. Productization is allowed, but product/public/security/legal/market claims require product evidence.
