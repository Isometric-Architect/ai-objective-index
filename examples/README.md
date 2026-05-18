# Examples

Future client and MCP usage examples will live here.

Examples should be read-only and should not implement payment, booking, login, email sending, form submission, purchase, or contract signing.

## REST API curl

After starting the API with `python -m ai_objective_index.api`:

```powershell
curl "http://localhost:8000/status"
```

```powershell
curl "http://localhost:8000/search?query=cheap%20image%20generation%20API"
```

The REST API is read-only and does not crawl URLs or perform external actions.
