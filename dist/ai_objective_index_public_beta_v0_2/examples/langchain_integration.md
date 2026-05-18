# LangChain Integration Notes

This is a lightweight conceptual example. It does not add a LangChain dependency.

## REST Tool Pattern

Create a small HTTP tool that calls the local AOI API:

```text
GET http://127.0.0.1:8000/search?query=cheap%20image%20generation%20API
```

Use the returned `objective_score`, `rank_reason`, `warnings`, and `missing_fields` as context for an agent response.

## Guardrail

The agent should preserve AOI's claim boundary:

- not a quality guarantee;
- not legal, financial, medical, or purchasing advice;
- no payment, booking, login, email, form submission, purchase, or contract execution.

