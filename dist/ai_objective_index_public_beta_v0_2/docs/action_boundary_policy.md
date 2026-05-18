# Action Boundary Policy

AOI v0.1 allows only read-only operations:

- `READ`
- `RANK`
- `COMPARE`
- `EXPLAIN`
- `QUOTE_SNIPPET`
- `DECISION_RECEIPT`

AOI v0.1 blocks:

- email
- booking
- payment
- login
- form submission
- purchase
- contract signing
- account connection

A decision receipt is not permission to perform external actions.
