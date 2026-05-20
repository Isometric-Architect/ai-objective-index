# PyPI Upload Instructions

1. Create or open the PyPI project owner account.
2. Create a scoped API token for `ai-objective-index`.
3. Do not paste the token into ChatGPT/Codex chat.
4. Do not commit the token.
5. Confirm:
   - `python -m ai_objective_index.package_metadata_audit`
   - `python -m ai_objective_index.pypi_publish_readiness`
   - `python -m ai_objective_index.no_secrets_audit`
   - `python -m ai_objective_index.launch_claim_guard`
6. Upload manually:

```powershell
python -m twine upload dist/*
```

7. Verify the package page and console scripts.
8. Rerun MCP Registry readiness.

Package 8P does not upload to PyPI.
