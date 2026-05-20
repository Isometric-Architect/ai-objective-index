# TestPyPI Upload Instructions

1. Create a TestPyPI account if needed.
2. Create a scoped upload API token.
3. Do not paste the token into ChatGPT/Codex chat.
4. Do not save the token in this repository.
5. Build locally:

```powershell
python -m ai_objective_index.pypi_publish_readiness
```

6. Upload manually:

```powershell
python -m twine upload --repository testpypi dist/*
```

7. Verify the TestPyPI package page.
8. Install from TestPyPI in a clean environment if desired.

No upload is performed by Package 8P.
