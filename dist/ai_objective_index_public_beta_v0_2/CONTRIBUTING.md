# Contributing

Thanks for helping shape AI Objective Index.

## Scope

Package 0 contributions should focus on:

- schemas;
- documentation;
- sample data contracts;
- scoring methodology;
- claim boundaries;
- future eval fixtures.

Do not add crawler, MCP server, payment, booking, login, email, form submission, purchase, or contract execution behavior in v0.1.

## Development Checks

Before submitting changes:

```powershell
python -m json.tool schemas/objective_request.schema.json
python -m json.tool data/sample_index.json
python -m pytest
```

Run `python -m pytest` only if tests exist or once a test suite is added.

## Sample Data Rules

- Keep fake sample objects realistic but clearly non-authoritative.
- Include missing fields when data is absent or unclear.
- Add source traces for fields that affect ranking.
- Do not imply that a trace is legal, procurement, financial, medical, or compliance advice.

## Claim Rules

Use bounded language. AOI may rank objective fit from available data and traces. AOI must not claim official-standard status, universal adoption, guaranteed quality, or automatic real-world action execution.

